#!/usr/bin/env python3
"""Sync design assets from the repository's single sources of truth into
deccan_convert/assets_data/, so the converter can bundle them.

Also produces deccan-document-base.docx: the Word template
templates/word/deccan-document.dotx re-zipped with its content type changed
from template.main+xml to document.main+xml, because python-docx can only
open documents, not templates. The result carries the .dotx's styles, theme,
and page setup verbatim.

Usage:
    python sync_assets.py           # copy / regenerate
    python sync_assets.py --check   # exit 1 if assets_data drifts from sources
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ASSETS = HERE / "deccan_convert" / "assets_data"

# Straight copies: repo-relative source -> assets_data file name.
COPY_MANIFEST = {
    "skill/assets/templates/document.html": "document.html",
    "skill/assets/logo.svg": "logo.svg",
    "skill/assets/logo.png": "logo.png",
    "templates/excel/deccan-workbook.xltx": "deccan-workbook.xltx",
    "templates/gworkspace/deccan-deck-for-drive.pptx": "deccan-deck.pptx",
}

DOTX_SOURCE = "templates/word/deccan-document.dotx"
DOCX_BASE = "deccan-document-base.docx"

_TEMPLATE_CT = (
    b"application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
)
_DOCUMENT_CT = (
    b"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
)


def build_base_docx(dotx: Path, out: Path) -> bytes:
    """Re-zip a .dotx as a .docx by swapping the main content type."""
    buf_entries = []
    with zipfile.ZipFile(dotx) as zin:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "[Content_Types].xml":
                if _TEMPLATE_CT not in data:
                    raise SystemExit(
                        f"{dotx}: expected template content type not found; "
                        "is this really a .dotx?"
                    )
                data = data.replace(_TEMPLATE_CT, _DOCUMENT_CT)
            buf_entries.append((info.filename, data))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in buf_entries:
            # Fixed date_time keeps the output byte-stable across runs so the
            # CI drift check can compare file contents directly.
            zi = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)
    return out.read_bytes()


def expected_files() -> dict[str, bytes]:
    """Compute the byte content every assets_data file should have."""
    result = {}
    for src_rel, dst_name in COPY_MANIFEST.items():
        src = REPO / src_rel
        if not src.is_file():
            raise SystemExit(f"Source asset missing: {src}")
        result[dst_name] = src.read_bytes()
    return result


def sync() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for dst_name, data in expected_files().items():
        (ASSETS / dst_name).write_bytes(data)
        print(f"  synced {dst_name}")
    build_base_docx(REPO / DOTX_SOURCE, ASSETS / DOCX_BASE)
    print(f"  built  {DOCX_BASE}")
    print(f"assets_data populated at {ASSETS}")


def check() -> None:
    problems = []
    for dst_name, data in expected_files().items():
        dst = ASSETS / dst_name
        if not dst.is_file():
            problems.append(f"missing: {dst_name}")
        elif dst.read_bytes() != data:
            problems.append(f"drift:   {dst_name} differs from its repo source")
    base = ASSETS / DOCX_BASE
    if not base.is_file():
        problems.append(f"missing: {DOCX_BASE}")
    else:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            fresh = build_base_docx(REPO / DOTX_SOURCE, tmp_path)
            if base.read_bytes() != fresh:
                problems.append(f"drift:   {DOCX_BASE} differs from regenerated output")
        finally:
            tmp_path.unlink(missing_ok=True)
    if problems:
        print("assets_data is out of sync with the repository sources:")
        for p in problems:
            print(f"  {p}")
        print("Run: python tools/converter/sync_assets.py")
        sys.exit(1)
    print("assets_data matches the repository sources.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify, do not write")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        sync()


if __name__ == "__main__":
    main()
