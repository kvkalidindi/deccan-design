"""Normalise arbitrary body HTML into the deccan-design component vocabulary.

Output is the {{BODY_HTML}} shape document-slots.md prescribes: one or more
<section class="section"> blocks, each opened by an <h1> with a
<span class="num">NN</span> eyebrow, containing only the components defined
in skill/references/components.md (paragraphs, h2-h4, lists, tables,
callouts, code blocks, pull quotes, links, inline code/strong/em, images).
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# Tags allowed to survive sanitisation, mapped to themselves (or dropped in
# favour of their children when set to None).
_ALLOWED = {
    "h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "table", "thead", "tbody",
    "tr", "th", "td", "pre", "code", "strong", "em", "b", "i", "a", "img",
    "br", "hr", "blockquote", "div", "span", "dl", "dt", "dd", "caption",
    "sup", "sub", "figure", "figcaption",
}

# Structural/scripting tags removed together with their content.
_STRIP_WITH_CONTENT = {"script", "style", "head", "nav", "iframe", "object",
                       "embed", "form", "button", "input", "select", "svg",
                       "noscript", "template", "footer", "header"}

# class values that carry deccan component semantics and must survive.
_KEPT_CLASSES = {
    "section", "lead", "callout", "muted", "label", "code-block", "pullquote",
    "num", "toc", "toc-label", "def", "figure", "figure-caption",
}

_KEPT_ATTRS = {
    "a": {"href"},
    "img": {"src", "alt"},
    "th": {"colspan", "rowspan"},
    "td": {"colspan", "rowspan"},
}

# Link schemes allowed to survive in <a href>. Everything else (javascript:,
# data:, file:, vbscript:, ...) is dropped so no active or local-file link is
# baked into the output.
_SAFE_HREF_PREFIXES = ("http:", "https:", "mailto:", "tel:", "#", "/", "./", "../")


def _sanitize_url_attrs(element: Tag, kept: dict) -> bool:
    """Neutralise dangerous URL attributes. Returns False if the whole element
    should be dropped.

    The produced HTML is rendered in a headless browser with network and
    file:// access, so a surviving remote/file <img src> would beacon out,
    reach internal hosts (SSRF), or probe the local filesystem at conversion
    time. Legitimate images arrive as inline data: URIs (mammoth), so images
    are restricted to data: and everything else is dropped. <a href> is
    scheme-allow-listed.
    """
    if element.name == "img":
        src = (kept.get("src") or "").strip()
        if not src.lower().startswith("data:image/"):
            return False  # drop remote/file/unknown image references entirely
    if element.name == "a" and "href" in kept:
        href = kept["href"].strip()
        # Collapse whitespace/control chars that could smuggle a scheme past
        # the prefix check (e.g. "java\tscript:").
        collapsed = "".join(href.split()).lower()
        if not collapsed.startswith(_SAFE_HREF_PREFIXES):
            kept.pop("href")
    return True


def sanitize_fragment(soup_fragment: Tag) -> None:
    """In-place: strip everything outside the component vocabulary."""
    for element in soup_fragment.find_all(list(_STRIP_WITH_CONTENT)):
        element.decompose()
    for comment in soup_fragment.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    for element in list(soup_fragment.find_all(True)):
        if element.name in ("h5", "h6"):
            element.name = "h4"
        elif element.name in ("section", "article", "main", "aside"):
            # Flatten foreign sectioning containers; deccan sections are
            # rebuilt from the heading structure afterwards.
            element.unwrap()
            continue
        elif element.name not in _ALLOWED:
            element.unwrap()
            continue

        kept = {}
        keep_attrs = _KEPT_ATTRS.get(element.name, set())
        classes = set(element.get("class", ())) & _KEPT_CLASSES
        if classes:
            kept["class"] = sorted(classes)
        for attr in keep_attrs:
            if element.has_attr(attr):
                kept[attr] = element[attr]
        if not _sanitize_url_attrs(element, kept):
            element.decompose()
            continue
        element.attrs = kept

    # b/i to semantic equivalents.
    for b in soup_fragment.find_all("b"):
        b.name = "strong"
    for i in soup_fragment.find_all("i"):
        i.name = "em"


def blockquotes_to_callouts(soup_fragment: Tag, soup: BeautifulSoup) -> None:
    """Map <blockquote> to the deccan callout component."""
    for quote in soup_fragment.find_all("blockquote"):
        quote.name = "div"
        quote["class"] = ["callout"]
        # Bare text inside the blockquote gets wrapped in a paragraph.
        for child in list(quote.children):
            if isinstance(child, NavigableString) and child.strip():
                p = soup.new_tag("p")
                child.wrap(p)


def code_blocks(soup_fragment: Tag) -> None:
    """Normalise <pre> to <pre class="code-block"> with no inner markup noise."""
    for pre in soup_fragment.find_all("pre"):
        text = pre.get_text()
        pre.clear()
        pre.string = text.rstrip("\n")
        pre["class"] = ["code-block"]


def normalise_tables(soup_fragment: Tag, soup: BeautifulSoup) -> None:
    """Ensure every table has a thead (component contract: mono-caps header)."""
    for table in soup_fragment.find_all("table"):
        if table.find("thead") is not None:
            continue
        first_row = table.find("tr")
        if first_row is None:
            continue
        if first_row.find("th") is not None:
            thead = soup.new_tag("thead")
            first_row.wrap(thead)
            table.insert(0, thead.extract())
        # Rows outside thead live in tbody.
        body_rows = [tr for tr in table.find_all("tr") if tr.find_parent("thead") is None]
        if body_rows and table.find("tbody") is None:
            tbody = soup.new_tag("tbody")
            body_rows[0].insert_before(tbody)
            for tr in body_rows:
                tbody.append(tr.extract())


def promote_first_paragraph_to_lead(section: Tag) -> None:
    """The paragraph directly after the section H1 becomes the lead."""
    h1 = section.find("h1")
    if h1 is None:
        return
    sibling = h1.find_next_sibling()
    if sibling is not None and sibling.name == "p" and "lead" not in sibling.get("class", ()):
        # Only promote a plausible thesis statement, not a long paragraph.
        if len(sibling.get_text(strip=True)) <= 260:
            sibling["class"] = ["lead"]


def build_sections(flat_html: str, *, lead_first_paragraph: bool = True) -> str:
    """Split sanitised flat HTML at each <h1> into numbered deccan sections.

    Content before the first h1 (if any) becomes an untitled opening section
    without a heading number.
    """
    soup = BeautifulSoup(f"<div id='root'>{flat_html}</div>", "html.parser")
    root = soup.find(id="root")

    sanitize_fragment(root)
    blockquotes_to_callouts(root, soup)
    code_blocks(root)
    normalise_tables(root, soup)

    # Partition children at h1 boundaries.
    groups: list[list] = [[]]
    for child in list(root.children):
        if isinstance(child, Tag) and child.name == "h1":
            groups.append([child])
        else:
            groups[-1].append(child)
    if not groups[0] or all(
        isinstance(c, NavigableString) and not c.strip() for c in groups[0]
    ):
        groups = groups[1:]

    if not groups:
        return ""

    out_soup = BeautifulSoup("", "html.parser")
    number = 0
    sections = []
    for group in groups:
        section = out_soup.new_tag("section", **{"class": "section"})
        has_h1 = bool(group) and isinstance(group[0], Tag) and group[0].name == "h1"
        if has_h1:
            number += 1
            h1 = group[0]
            if h1.find("span", class_="num") is None:
                num = out_soup.new_tag("span", **{"class": "num"})
                num.string = f"{number:02d}"
                h1.insert(0, num)
        for child in group:
            section.append(child.extract() if isinstance(child, Tag) else NavigableString(str(child)))
        if lead_first_paragraph and has_h1:
            promote_first_paragraph_to_lead(section)
        sections.append(section)

    return "\n\n".join(str(s) for s in sections)
