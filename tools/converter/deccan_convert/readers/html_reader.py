"""HTML reader: .html file -> DocumentIR.

Two paths:
- An existing deccan-design document (detected by its cover markup) is
  "re-poured": metadata lifts from the cover metadata strip and the body
  sections are re-normalised, which upgrades old documents into the current
  bundled template.
- Foreign HTML is sanitised down to the component vocabulary; metadata comes
  from <title> and <meta> tags where present.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from deccan_convert.ir import CLASSIFICATIONS, DOCUMENT_TYPES, DocumentIR, Metadata
from deccan_convert.readers._sections import build_sections

_COVER_META_LABELS = {
    "document type": "document_type",
    "prepared by": "prepared_by",
    "date": "date",
    "version": "version",
    "classification": "classification",
}


def read_html(path: Path) -> DocumentIR:
    soup = BeautifulSoup(path.read_text(encoding="utf-8-sig"), "html.parser")
    if soup.find(class_="cover") is not None:
        return _read_deccan_document(soup)
    return _read_foreign_html(soup)


def _read_deccan_document(soup: BeautifulSoup) -> DocumentIR:
    metadata = Metadata()
    cover = soup.find(class_="cover")

    title_el = cover.find(class_="cover-title") or cover.find("h1")
    if title_el is not None:
        metadata.title = title_el.get_text(strip=True)
    subtitle_el = cover.find(class_="cover-subtitle")
    if subtitle_el is not None:
        metadata.subtitle = subtitle_el.get_text(strip=True)

    meta_strip = soup.find(class_="cover-meta")
    if meta_strip is not None:
        for dt in meta_strip.find_all("dt"):
            field = _COVER_META_LABELS.get(dt.get_text(strip=True).lower())
            dd = dt.find_next_sibling("dd") or (dt.parent.find("dd") if dt.parent else None)
            if field and dd is not None:
                setattr(metadata, field, dd.get_text(strip=True))

    body_root = soup.find("main") or soup.body or soup
    parts = []
    for section in body_root.find_all("section", class_="section"):
        # Strip the existing numbering; build_sections re-numbers.
        for num in section.find_all("span", class_="num"):
            num.decompose()
        parts.append(section.decode_contents())
    if not parts:
        # A deccan cover without recognisable sections — treat the main
        # content as foreign flat HTML.
        for cls in ("cover", "end-page"):
            for el in soup.find_all(class_=cls):
                el.decompose()
        parts = [(soup.find("main") or soup.body or soup).decode_contents()]

    return DocumentIR(metadata=metadata, body_html=build_sections("\n".join(parts)))


def _read_foreign_html(soup: BeautifulSoup) -> DocumentIR:
    metadata = Metadata()
    warnings: list[str] = []

    if soup.title is not None and soup.title.string:
        metadata.title = soup.title.string.strip()
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta is not None and author_meta.get("content"):
        metadata.prepared_by = author_meta["content"].strip()
    for name in ("classification", "category"):
        tag = soup.find("meta", attrs={"name": name})
        if tag is None or not tag.get("content"):
            continue
        value = tag["content"].strip().title()
        if name == "classification" and value in CLASSIFICATIONS:
            metadata.classification = value
        elif name == "category" and value in DOCUMENT_TYPES:
            metadata.document_type = value

    body_root = (
        soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    # If the first heading equals the document title, drop it — the cover
    # carries the title.
    first_heading = body_root.find(["h1", "h2"])
    if (
        first_heading is not None
        and metadata.title
        and first_heading.get_text(strip=True) == metadata.title
    ):
        first_heading.decompose()

    return DocumentIR(
        metadata=metadata,
        body_html=build_sections(body_root.decode_contents()),
        warnings=warnings,
    )
