"""DOCX reader: .docx file -> DocumentIR.

mammoth converts the document to semantic HTML, deliberately discarding the
source visual formatting — the design system supplies the presentation.
Metadata comes from the Word core properties. Word documents exported from
Google Docs (File > Download > .docx) take the same path.
"""

from __future__ import annotations

from pathlib import Path

import mammoth
from docx import Document

from deccan_convert.ir import DOCUMENT_TYPES, DocumentIR, Metadata
from deccan_convert.limits import guard_no_doctype, guard_zip
from deccan_convert.readers._sections import build_sections

# Word style names (including the deccan .dotx custom styles) -> components.
_STYLE_MAP = """
p[style-name='Lead'] => p.lead:fresh
p[style-name='Callout Default'] => div.callout > p:fresh
p[style-name='Callout Muted'] => div.callout.muted > p:fresh
p[style-name='Code Block'] => pre:separator('\\n')
p[style-name='Quote'] => blockquote > p:fresh
p[style-name='Intense Quote'] => div.pullquote > p:fresh
r[style-name='Code Inline'] => code
"""


def read_docx(path: Path) -> DocumentIR:
    warnings: list[str] = []

    # docx is a ZIP; guard against decompression bombs, and reject a DTD in
    # document.xml (mammoth's minidom parser expands internal entities).
    guard_zip(path)
    guard_no_doctype(path, "word/document.xml")

    with open(path, "rb") as fh:
        result = mammoth.convert_to_html(fh, style_map=_STYLE_MAP)
    for message in result.messages:
        if message.type == "warning" and "style" not in message.message.lower():
            warnings.append(f"docx: {message.message}")

    metadata = _metadata_from_core_properties(path)
    html = result.value

    doc_title = metadata.title
    if doc_title:
        # Drop a leading heading that duplicates the title; the cover carries it.
        import re

        pattern = rf"\A\s*<h[12][^>]*>\s*{re.escape(doc_title)}\s*</h[12]>"
        html = re.sub(pattern, "", html, count=1)

    return DocumentIR(
        metadata=metadata,
        body_html=build_sections(html),
        warnings=warnings,
    )


def _metadata_from_core_properties(path: Path) -> Metadata:
    metadata = Metadata()
    try:
        props = Document(str(path)).core_properties
    except Exception:
        return metadata
    if props.title:
        metadata.title = props.title.strip()
    if props.subject:
        metadata.subtitle = props.subject.strip()
    if props.author:
        metadata.prepared_by = props.author.strip()
    if props.category and props.category.strip().title() in DOCUMENT_TYPES:
        metadata.document_type = props.category.strip().title()
    if props.version:
        metadata.version = str(props.version).strip()
    return metadata
