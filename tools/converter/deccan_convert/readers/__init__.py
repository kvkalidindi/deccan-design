from __future__ import annotations

from pathlib import Path

from deccan_convert.ir import DocumentIR


def read_document(path: Path, input_format: str) -> DocumentIR:
    """Dispatch to the reader for a Track A (document) format."""
    if input_format == "md":
        from deccan_convert.readers.md_reader import read_md

        return read_md(path)
    if input_format == "html":
        from deccan_convert.readers.html_reader import read_html

        return read_html(path)
    if input_format == "docx":
        from deccan_convert.readers.docx_reader import read_docx

        return read_docx(path)
    if input_format == "pdf":
        from deccan_convert.readers.pdf_reader import read_pdf

        return read_pdf(path)
    raise ValueError(f"No document reader for format '{input_format}'")
