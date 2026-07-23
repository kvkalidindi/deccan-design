#!/usr/bin/env python3
"""Sync design assets from the repository's single sources of truth into
deccan_convert/assets_data/, so the converter can bundle them.

Two asset groups:

1. Flat runtime assets — files the converter's writers load at runtime
   (slot template, logos, style bases). This includes a base .docx for every
   Word template: the .dotx re-zipped with its content type changed from
   template.main+xml to document.main+xml, because python-docx can only open
   documents, not templates. The result carries the .dotx's styles, theme,
   page setup, and footer contract verbatim.

2. The kit tree (assets_data/kit/) — verbatim copies of the full template
   suite and the Claude skill, written out by `deccan-convert --export-kit`
   so a single downloaded binary can equip an offline endpoint with the
   complete design system.

Usage:
    python sync_assets.py           # copy / regenerate
    python sync_assets.py --check   # exit 1 if assets_data drifts from sources
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ASSETS = HERE / "deccan_convert" / "assets_data"
KIT = ASSETS / "kit"

# Flat runtime assets: repo-relative source -> assets_data file name.
COPY_MANIFEST = {
    "skill/assets/templates/document.html": "document.html",
    "skill/assets/logo.svg": "logo.svg",
    "skill/assets/logo.png": "logo.png",
    "skill/assets/logo.b64.txt": "logo.b64.txt",
    "templates/excel/deccan-workbook.xltx": "deccan-workbook.xltx",
    "templates/gworkspace/deccan-deck-for-drive.pptx": "deccan-deck.pptx",
}

# Word templates that get a python-docx-openable base derived from the .dotx.
DOTX_BASES = {
    "templates/word/deccan-document.dotx": "deccan-document-base.docx",
    "templates/word/deccan-technical-spec.dotx": "deccan-technical-spec-base.docx",
    "templates/word/deccan-policy.dotx": "deccan-policy-base.docx",
    "templates/word/deccan-customer-letter.dotx": "deccan-customer-letter-base.docx",
}

# Kit tree: repo-relative sources copied verbatim under assets_data/kit/
# with the same repo-relative layout (templates/... and skill/...).
KIT_MANIFEST = [
    "templates/word/deccan-document.dotx",
    "templates/word/deccan-technical-spec.dotx",
    "templates/word/deccan-policy.dotx",
    "templates/word/deccan-customer-letter.dotx",
    "templates/excel/deccan-workbook.xltx",
    "templates/excel/deccan-comparison.xltx",
    "templates/excel/deccan-financial-model.xltx",
    "templates/powerpoint/deccan-deck.potx",
    "templates/powerpoint/deccan-customer-pitch.potx",
    "templates/powerpoint/deccan-internal-review.potx",
    "templates/gworkspace/deccan-document-for-drive.docx",
    "templates/gworkspace/deccan-workbook-for-drive.xlsx",
    "templates/gworkspace/deccan-deck-for-drive.pptx",
    "templates/gworkspace/deccan-gmail-signature.html",
    "templates/gworkspace/README.md",
    "templates/outlook/deccan-signature.htm",
    "templates/outlook/deccan-signature.txt",
    "skill/SKILL.md",
    "skill/references/tokens.md",
    "skill/references/components.md",
    "skill/references/print-rules.md",
    "skill/references/tone-and-voice.md",
    "skill/references/document-templates.md",
    "skill/assets/logo.svg",
    "skill/assets/logo.png",
    "skill/assets/logo.b64.txt",
    "skill/assets/templates/document.html",
    "skill/assets/templates/document-slots.md",
    "skill/assets/templates/README.md",
]

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


def _zip_contents_equal(a: bytes, b: bytes) -> bool:
    """True when two zip packages hold the same entries with the same bytes."""
    import io

    with zipfile.ZipFile(io.BytesIO(a)) as za, zipfile.ZipFile(io.BytesIO(b)) as zb:
        names_a = [i.filename for i in za.infolist()]
        names_b = [i.filename for i in zb.infolist()]
        if names_a != names_b:
            return False
        return all(za.read(n) == zb.read(n) for n in names_a)


def expected_copies() -> dict[Path, bytes]:
    """Every straight-copy destination (flat + kit) -> expected bytes."""
    result: dict[Path, bytes] = {}
    for src_rel, dst_name in COPY_MANIFEST.items():
        src = REPO / src_rel
        if not src.is_file():
            raise SystemExit(f"Source asset missing: {src}")
        result[ASSETS / dst_name] = src.read_bytes()
    for src_rel in KIT_MANIFEST:
        src = REPO / src_rel
        if not src.is_file():
            raise SystemExit(f"Kit source missing: {src}")
        result[KIT / src_rel] = src.read_bytes()
    return result


def sync() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for dst, data in expected_copies().items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print(f"  synced {dst.relative_to(ASSETS)}")
    for src_rel, base_name in DOTX_BASES.items():
        build_base_docx(REPO / src_rel, ASSETS / base_name)
        print(f"  built  {base_name}")
    print(f"assets_data populated at {ASSETS}")


def check() -> None:
    problems = []
    for dst, data in expected_copies().items():
        rel = dst.relative_to(ASSETS)
        if not dst.is_file():
            problems.append(f"missing: {rel}")
        elif dst.read_bytes() != data:
            problems.append(f"drift:   {rel} differs from its repo source")

    import tempfile

    for src_rel, base_name in DOTX_BASES.items():
        base = ASSETS / base_name
        if not base.is_file():
            problems.append(f"missing: {base_name}")
            continue
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            fresh = build_base_docx(REPO / src_rel, tmp_path)
            # Compare zip CONTENTS, not raw bytes: DEFLATE output differs
            # across zlib builds (e.g. the Windows CI runner), so a committed
            # base and a freshly regenerated one may differ byte-wise while
            # being identical in every entry.
            if not _zip_contents_equal(base.read_bytes(), fresh):
                problems.append(f"drift:   {base_name} differs from regenerated output")
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
