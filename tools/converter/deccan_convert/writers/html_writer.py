"""HTML writer: DocumentIR -> styled deccan-design HTML.

Fills the placeholders of the bundled formal document.html exactly as
document-slots.md prescribes, including the document-control page (v2.7.0)
with its stated defaults — never an invented name. The surrounding markup and CSS (tokens, print
contract, @media print overrides) are never modified.
"""

from __future__ import annotations

import html as html_escape
from pathlib import Path

from deccan_convert.assets import asset_text
from deccan_convert.ir import DocumentIR

_TEXT_MARK = '<div class="mark-rule"></div>\n    <div class="mark-text">Deccan Fine Chemicals</div>'


def render_html(ir: DocumentIR, logo: bool = False) -> str:
    meta = ir.metadata.with_defaults()
    missing = meta.missing_required()
    if missing:
        raise ValueError(
            "Missing required document details: " + ", ".join(missing) + ". "
            "These are never invented — provide them explicitly."
        )
    template = asset_text("document.html")
    if logo:
        # Cover mark only: the graphical wordmark from the bundled asset as a
        # data URI (nothing is fetched). The template's own .mark-logo class
        # (36px height) styles it; the end page keeps the text mark.
        b64 = asset_text("logo.b64.txt").strip()
        template = template.replace(
            _TEXT_MARK,
            f'<img class="mark-logo" alt="Deccan Fine Chemicals" '
            f'src="data:image/png;base64,{b64}">',
            1,
        )
    esc = html_escape.escape
    revision_row = (
        f"<tr><td>{esc(meta.version)}</td><td>{esc(meta.date)}</td>"
        f"<td>{esc(meta.prepared_by)}</td><td>Initial issue</td>"
        f"<td>Pending approval</td></tr>"
    )
    return (
        template.replace("{{DOCUMENT_ID}}", "Not assigned")
        .replace("{{OWNER}}", esc(meta.prepared_by))
        .replace("{{APPROVER}}", "Pending approval")
        .replace("{{EFFECTIVE_DATE}}", esc(meta.date))
        .replace("{{REVIEW_CYCLE}}", "Not set")
        .replace("{{REVISION_ROWS}}", revision_row)
        .replace("{{TITLE}}", esc(meta.title))
        .replace("{{SUBTITLE}}", esc(meta.subtitle))
        .replace("{{DOCUMENT_TYPE}}", esc(meta.document_type))
        .replace("{{PREPARED_BY}}", esc(meta.prepared_by))
        .replace("{{DATE}}", esc(meta.date))
        .replace("{{VERSION}}", esc(meta.version))
        .replace("{{CLASSIFICATION}}", esc(meta.classification))
        .replace("{{BODY_HTML}}", ir.body_html)
    )


def write_html(ir: DocumentIR, path: Path, logo: bool = False) -> Path:
    path.write_text(render_html(ir, logo=logo), encoding="utf-8")
    return path
