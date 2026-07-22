"""Markdown reader: .md file -> DocumentIR.

Metadata comes from an optional YAML front-matter block; otherwise the first
top-level '#' heading becomes the title. Heading levels are shifted so body
sections open at <h1> per the template contract when the title heading is
consumed.
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

from deccan_convert.ir import DocumentIR, Metadata
from deccan_convert.readers._sections import build_sections

_FRONT_MATTER_KEYS = {
    "title": "title",
    "subtitle": "subtitle",
    "type": "document_type",
    "document_type": "document_type",
    "document-type": "document_type",
    "author": "prepared_by",
    "prepared_by": "prepared_by",
    "prepared-by": "prepared_by",
    "date": "date",
    "version": "version",
    "classification": "classification",
}


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Parse a leading simple 'key: value' YAML block. Returns (fields, rest).

    Deliberately minimal — flat scalar keys only, no PyYAML dependency.
    """
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if match is None:
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip() != line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip().strip("'\"")
        target = _FRONT_MATTER_KEYS.get(key)
        if target and value:
            fields[target] = value
    return fields, text[match.end():]


def read_md(path: Path) -> DocumentIR:
    text = path.read_text(encoding="utf-8-sig")
    fields, body_md = _parse_front_matter(text)
    metadata = Metadata(**fields)
    warnings: list[str] = []

    html = markdown.markdown(
        body_md,
        extensions=["extra", "sane_lists"],
        output_format="html",
    )

    # Without a front-matter title, consume a leading H1 as the title and
    # promote the remaining heading levels by one.
    if not metadata.title:
        m = re.match(r"\s*<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
        if m:
            metadata.title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            html = html[m.end():]
            html = _promote_headings(html)

    if "<h1" not in html:
        # No section headings at all — a single untitled section still works,
        # but sections read better with a heading when the title exists.
        pass

    return DocumentIR(
        metadata=metadata,
        body_html=build_sections(html),
        warnings=warnings,
    )


def _promote_headings(html: str) -> str:
    """h2->h1 ... h6->h5 after the document title heading is consumed."""
    for level in range(2, 7):
        html = re.sub(rf"<(/?)h{level}(\s[^>]*)?>", rf"<\1h{level - 1}\2>", html)
    return html
