from __future__ import annotations

from pathlib import Path
from typing import Callable

from deccan_convert.ir import DocumentIR


def write_document(
    ir: DocumentIR,
    path: Path,
    output_format: str,
    log: Callable[[str], None] | None = None,
    template: str = "document",
    logo: bool = False,
) -> Path:
    """Dispatch to the writer for a Track A (document) format.

    Returns the path actually written — normally `path`, but the PDF writer
    falls back to a styled .html when no Chromium browser is available.
    `template` selects the Word template flavor (docx output only); `logo`
    swaps the cover's text wordmark for the bundled graphical mark.
    """
    if output_format == "html":
        from deccan_convert.writers.html_writer import write_html

        return write_html(ir, path, logo=logo)
    if output_format == "md":
        from deccan_convert.writers.md_writer import write_md

        return write_md(ir, path)
    if output_format == "docx":
        from deccan_convert.writers.docx_writer import write_docx

        return write_docx(ir, path, template=template, logo=logo)
    if output_format == "pdf":
        from deccan_convert.writers.pdf_writer import write_pdf

        return write_pdf(ir, path, log=log, logo=logo)
    raise ValueError(f"No document writer for format '{output_format}'")
