"""Resource-exhaustion guards for untrusted input.

The converter opens attacker-controlled documents. The Office/PDF libraries
do not bound decompression, declared sheet dimensions, entity expansion, or
page counts, so a small crafted file can drive the process to OOM or a
multi-minute hang. These guards run cheap, up-front checks before any heavy
library call. Limits are generous for real documents and only stop abuse.
"""

from __future__ import annotations

import zipfile
from pathlib import Path


class InputTooLarge(ValueError):
    """Raised when an input exceeds a safety limit (never a valid document)."""


# Raw input-file size cap (applies to every format).
MAX_INPUT_BYTES = 100 * 1024 * 1024  # 100 MB

# ZIP (docx/xlsx/pptx) decompression guards.
MAX_ZIP_TOTAL_UNCOMPRESSED = 512 * 1024 * 1024  # 512 MB summed across entries
MAX_ZIP_ENTRY_UNCOMPRESSED = 256 * 1024 * 1024  # 256 MB for any single entry
MAX_ZIP_ENTRIES = 4096
MAX_ZIP_RATIO = 200  # decompressed/compressed for a single entry

# Spreadsheet styled-region cap (openpyxl materialises the declared rectangle).
MAX_XLSX_ROWS = 50_000
MAX_XLSX_COLS = 256

# PDF page cap.
MAX_PDF_PAGES = 500

# Base64 data-URI image payload cap (encoded length) before decode.
MAX_DATA_URI_B64 = 8_000_000  # ~6 MB decoded


def guard_input_size(path: Path, max_bytes: int | None = None) -> None:
    # Resolve the limit at call time (not as a bound default) so it stays
    # overridable and reflects the module constant.
    max_bytes = MAX_INPUT_BYTES if max_bytes is None else max_bytes
    size = Path(path).stat().st_size
    if size > max_bytes:
        raise InputTooLarge(
            f"Input file is {size / 1_048_576:.0f} MB, over the "
            f"{max_bytes // 1_048_576} MB limit. Refusing to process it."
        )


def guard_zip(path: Path) -> None:
    """Reject decompression-bomb ZIP containers (docx/xlsx/pptx)."""
    guard_input_size(path)
    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
    except zipfile.BadZipFile as exc:
        raise InputTooLarge(f"Not a valid Office file: {exc}") from None

    if len(infos) > MAX_ZIP_ENTRIES:
        raise InputTooLarge(
            f"Office file has {len(infos)} internal entries, over the "
            f"{MAX_ZIP_ENTRIES} limit (possible zip bomb)."
        )
    total = 0
    for info in infos:
        total += info.file_size
        if info.file_size > MAX_ZIP_ENTRY_UNCOMPRESSED:
            raise InputTooLarge(
                f"Office file entry '{info.filename}' decompresses to "
                f"{info.file_size / 1_048_576:.0f} MB (possible zip bomb)."
            )
        if info.compress_size > 0 and info.file_size / info.compress_size > MAX_ZIP_RATIO:
            raise InputTooLarge(
                f"Office file entry '{info.filename}' has a "
                f"{info.file_size // max(info.compress_size, 1)}x compression "
                "ratio (possible zip bomb)."
            )
    if total > MAX_ZIP_TOTAL_UNCOMPRESSED:
        raise InputTooLarge(
            f"Office file decompresses to {total / 1_048_576:.0f} MB total, "
            f"over the {MAX_ZIP_TOTAL_UNCOMPRESSED // 1_048_576} MB limit "
            "(possible zip bomb)."
        )


def guard_no_doctype(path: Path, member: str) -> None:
    """Reject an Office part carrying a DTD/entity declaration.

    mammoth parses word/document.xml with minidom/expat, which expands
    internal entities (billion-laughs). Well-formed OOXML never declares a
    DOCTYPE, so rejecting one costs nothing and closes the expansion vector.
    """
    try:
        with zipfile.ZipFile(path) as zf:
            head = zf.read(member)[:4096].lstrip()
    except (KeyError, zipfile.BadZipFile):
        return
    lowered = head.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise InputTooLarge(
            f"'{member}' declares a DTD/entity, which valid Office files never "
            "do. Refusing to process it (entity-expansion protection)."
        )
