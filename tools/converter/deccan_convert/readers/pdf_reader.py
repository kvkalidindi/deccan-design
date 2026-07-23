"""PDF reader: .pdf file -> DocumentIR. Text extraction only.

PDF input is content rescue into the design system, not round-tripping:
no OCR, images are dropped, and multi-column layouts may interleave. The
reader attaches an explicit fidelity warning to every result.

Heading detection clusters the character font sizes on each page: the most
common size is body text; markedly larger lines become h1/h2 candidates.
"""

from __future__ import annotations

import html
import re
from collections import Counter
from pathlib import Path

import pdfplumber

from deccan_convert.ir import DocumentIR, Metadata
from deccan_convert.limits import MAX_PDF_PAGES, guard_input_size

FIDELITY_WARNING = (
    "PDF input is text extraction only: images are dropped, exact styling is "
    "not preserved, and multi-column layouts may interleave. For best results "
    "convert the original source document."
)

_FOOTER_RE = re.compile(
    r"^\s*(Deccan Fine Chemicals\s*[·.]\s*Confidential(\s+\d{1,4})?|\d{1,4})\s*$"
)


def read_pdf(path: Path) -> DocumentIR:
    warnings = [FIDELITY_WARNING]
    metadata = Metadata()

    # Bound the untrusted PDF: raw size, and the number of pages actually
    # parsed (pdfminer has quadratic/recursive DoS history on crafted files).
    guard_input_size(path)

    lines: list[tuple[float, str]] = []  # (font size, text)
    body_size = 12.0
    with pdfplumber.open(path) as pdf:
        info = pdf.metadata or {}
        if info.get("Title"):
            metadata.title = str(info["Title"]).strip()
        if info.get("Author"):
            metadata.prepared_by = str(info["Author"]).strip()

        pages = pdf.pages
        if len(pages) > MAX_PDF_PAGES:
            warnings.append(
                f"PDF has {len(pages)} pages; only the first {MAX_PDF_PAGES} "
                "were processed."
            )
            pages = pages[:MAX_PDF_PAGES]

        size_counter: Counter[float] = Counter()
        page_lines: list[list[tuple[float, str]]] = []
        for page in pages:
            current: list[tuple[float, str]] = []
            words = page.extract_words(extra_attrs=["size", "top"])
            if not words:
                page_lines.append(current)
                continue
            # Group words into visual lines by their vertical position.
            row: list[dict] = []
            row_top = None
            for word in sorted(words, key=lambda w: (round(w["top"], 1), w["x0"])):
                if row_top is None or abs(word["top"] - row_top) <= 2.5:
                    row.append(word)
                    row_top = word["top"] if row_top is None else row_top
                else:
                    current.append(_finish_row(row))
                    row = [word]
                    row_top = word["top"]
            if row:
                current.append(_finish_row(row))
            for size, text in current:
                if text:
                    size_counter[round(size, 1)] += len(text)
            page_lines.append(current)

        if size_counter:
            body_size = size_counter.most_common(1)[0][0]
        for current in page_lines:
            for size, text in current:
                if not text or _FOOTER_RE.match(text):
                    continue
                lines.append((size, text))

    if not lines:
        raise ValueError(
            "This PDF contains no extractable text (it may be a scanned "
            "image). OCR is not supported; convert the original source "
            "document instead."
        )

    html_parts: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            html_parts.append(f"<p>{html.escape(' '.join(paragraph))}</p>")
            paragraph.clear()

    for size, text in lines:
        level = _heading_level(size, body_size)
        if level is not None and len(text) <= 120:
            flush_paragraph()
            html_parts.append(f"<h{level}>{html.escape(text)}</h{level}>")
        elif _looks_like_bullet(text):
            flush_paragraph()
            html_parts.append(f"<ul><li>{html.escape(_strip_bullet(text))}</li></ul>")
        else:
            paragraph.append(text)
            if text.rstrip().endswith((".", ":", "!", "?", '."', ".'")):
                flush_paragraph()
    flush_paragraph()

    body = "\n".join(html_parts)
    # Merge adjacent single-item lists produced line by line.
    body = body.replace("</li></ul>\n<ul><li>", "</li>\n<li>")

    if not metadata.title:
        # First h1/h2 line is the best available title guess for the GUI to
        # pre-fill; it stays in the body (it may be a real section heading).
        m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body)
        if m:
            metadata.title = html.unescape(m.group(1))

    return DocumentIR(metadata=metadata, body_html=_wrap(body), warnings=warnings)


def _finish_row(row: list[dict]) -> tuple[float, str]:
    text = " ".join(w["text"] for w in sorted(row, key=lambda w: w["x0"])).strip()
    size = max((w.get("size") or 0) for w in row)
    return (float(size), text)


def _heading_level(size: float, body_size: float) -> int | None:
    if size >= body_size * 1.6:
        return 1
    if size >= body_size * 1.3:
        return 2
    if size >= body_size * 1.15:
        return 3
    return None


_BULLET_RE = re.compile(r"^\s*([•▪●○◦·\-–—*]|\d{1,2}[.)])\s+")


def _looks_like_bullet(text: str) -> bool:
    return _BULLET_RE.match(text) is not None


def _strip_bullet(text: str) -> str:
    return _BULLET_RE.sub("", text).strip()


def _wrap(flat_html: str) -> str:
    from deccan_convert.readers._sections import build_sections

    return build_sections(flat_html)
