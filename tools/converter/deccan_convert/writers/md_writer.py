"""Markdown writer: DocumentIR -> .md with YAML front matter.

Markdown carries no visual styling, so "applying the design" here means the
structural conventions travel: front-matter metadata, section headings at
'#', callouts as blockquotes, code fenced. Converting the .md back through
this tool reproduces the styled formats.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify

from deccan_convert.ir import DocumentIR


def render_md(ir: DocumentIR) -> str:
    meta = ir.metadata.with_defaults()
    front = ["---"]
    front.append(f"title: {_yaml(meta.title)}")
    if meta.subtitle:
        front.append(f"subtitle: {_yaml(meta.subtitle)}")
    if meta.document_type:
        front.append(f"type: {_yaml(meta.document_type)}")
    if meta.prepared_by:
        front.append(f"author: {_yaml(meta.prepared_by)}")
    front.append(f"date: {_yaml(meta.date)}")
    front.append(f"version: {_yaml(meta.version)}")
    front.append(f"classification: {_yaml(meta.classification)}")
    front.append("---")

    soup = BeautifulSoup(ir.body_html, "html.parser")
    # Section numbering eyebrows are a rendered artefact, not content.
    for num in soup.find_all("span", class_="num"):
        num.decompose()
    # Callouts read naturally as blockquotes in markdown.
    for callout in soup.find_all("div", class_="callout"):
        callout.name = "blockquote"
    for quote in soup.find_all("div", class_="pullquote"):
        quote.name = "blockquote"

    body = markdownify(str(soup), heading_style="ATX", bullets="-")
    body = "\n".join(line.rstrip() for line in body.splitlines())
    while "\n\n\n" in body:
        body = body.replace("\n\n\n", "\n\n")

    return "\n".join(front) + "\n\n" + body.strip() + "\n"


def _yaml(value: str) -> str:
    if any(ch in value for ch in ":#'\"[]{}|>&*!%@`"):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def write_md(ir: DocumentIR, path: Path) -> Path:
    path.write_text(render_md(ir), encoding="utf-8")
    return path
