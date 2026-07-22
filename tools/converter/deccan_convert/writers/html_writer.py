"""HTML writer: DocumentIR -> styled deccan-design HTML.

Fills the eight placeholders of the bundled document.html exactly as
document-slots.md prescribes. The surrounding markup and CSS (tokens, print
contract, @media print overrides) are never modified.
"""

from __future__ import annotations

import html as html_escape
from pathlib import Path

from deccan_convert.assets import asset_text
from deccan_convert.ir import DocumentIR


def render_html(ir: DocumentIR) -> str:
    meta = ir.metadata.with_defaults()
    missing = meta.missing_required()
    if missing:
        raise ValueError(
            "Missing required document details: " + ", ".join(missing) + ". "
            "These are never invented — provide them explicitly."
        )
    template = asset_text("document.html")
    esc = html_escape.escape
    return (
        template.replace("{{TITLE}}", esc(meta.title))
        .replace("{{SUBTITLE}}", esc(meta.subtitle))
        .replace("{{DOCUMENT_TYPE}}", esc(meta.document_type))
        .replace("{{PREPARED_BY}}", esc(meta.prepared_by))
        .replace("{{DATE}}", esc(meta.date))
        .replace("{{VERSION}}", esc(meta.version))
        .replace("{{CLASSIFICATION}}", esc(meta.classification))
        .replace("{{BODY_HTML}}", ir.body_html)
    )


def write_html(ir: DocumentIR, path: Path) -> Path:
    path.write_text(render_html(ir), encoding="utf-8")
    return path
