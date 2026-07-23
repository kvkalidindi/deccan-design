#!/usr/bin/env python3
"""Read-only compliance scan of the deccan-design template suite.

Checks every template artifact against the tokens and furniture rules
(skill/references/tokens.md, skill/SKILL.md) and the converter's marker
contract. Exit 1 on any violation — wired into CI.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deccan_tokens as T

REPO = Path(__file__).resolve().parent.parent.parent
TEMPLATES = REPO / "templates"

OOXML_FILES = [
    *(TEMPLATES / "word").glob("*.dotx"),
    *(TEMPLATES / "excel").glob("*.xltx"),
    *(TEMPLATES / "powerpoint").glob("*.potx"),
    TEMPLATES / "gworkspace" / "deccan-document-for-drive.docx",
    TEMPLATES / "gworkspace" / "deccan-workbook-for-drive.xlsx",
    TEMPLATES / "gworkspace" / "deccan-deck-for-drive.pptx",
]

TEXT_FILES = [
    TEMPLATES / "outlook" / "deccan-signature.htm",
    TEMPLATES / "outlook" / "deccan-signature.txt",
    TEMPLATES / "gworkspace" / "deccan-gmail-signature.html",
    REPO / "skill" / "assets" / "templates" / "document.html",
]

# Word-boundary face patterns. "Times" alone would hit "Sometimes"; anchor it.
# "Cambria(?! Math)": Cambria Math is the equation-layout font in Word's
# m:mathFont setting — the only widely available OpenType math face — and is
# not a text face, so it is exempt from the text-face ban.
_BANNED_RE = re.compile(
    r"\b(Helvetica|Univers|Arial|Calibri|Cambria(?! Math)|Verdana|Times New Roman|"
    r"Garamond|Georgia|Courier|Lucida Console)\b",
    re.IGNORECASE,
)
_STALE_RE = re.compile("|".join(T.STALE_HEXES), re.IGNORECASE)

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def xml_parts(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as zf:
        return {
            n: zf.read(n).decode("utf-8", errors="replace")
            for n in zf.namelist()
            if n.endswith(".xml")
        }


def check_ooxml(path: Path) -> None:
    rel = path.relative_to(REPO)
    parts = xml_parts(path)
    for name, xml in parts.items():
        for match in _BANNED_RE.finditer(xml):
            fail(f"{rel}::{name}: banned face '{match.group(0)}'")
        # Excel's fixed legacy <indexedColors> palette is a mandated 56-color
        # lookup table, not applied styling — exempt from the stale-hex scan.
        scannable = re.sub(r"<indexedColors>.*?</indexedColors>", "", xml, flags=re.DOTALL)
        stale = sorted({m.group(0).upper() for m in _STALE_RE.finditer(scannable)})
        if stale:
            fail(f"{rel}::{name}: stale Office hex(es) {stale}")

    theme_name = next((n for n in parts if n.endswith("theme/theme1.xml")), None)
    if theme_name is None:
        fail(f"{rel}: no theme1.xml")
        return
    theme = parts[theme_name]
    if f'<a:accent1><a:srgbClr val="{T.DECCAN_BLUE}"/></a:accent1>' not in theme:
        fail(f"{rel}: theme accent1 is not Deccan Blue")
    if f'<a:latin typeface="{T.SANS_DISPLAY}"/>' not in theme:
        fail(f"{rel}: theme majorFont is not {T.SANS_DISPLAY}")

    if "word/document.xml" in parts:
        _check_word(rel, parts)
    elif any(n.startswith("xl/") for n in parts):
        _check_excel(rel, parts)
    elif any(n.startswith("ppt/") for n in parts):
        _check_ppt(rel, parts)
    ok(f"{rel}")


def _check_word(rel, parts) -> None:
    footer = parts.get("word/footer1.xml", "")
    if T.FOOTER_TEXT not in footer:
        fail(f"{rel}: footer1 missing '{T.FOOTER_TEXT}'")
    if " PAGE " not in footer or "fldChar" not in footer:
        fail(f"{rel}: footer1 missing PAGE field")
    if '<w:tab w:pos="9936" w:val="right"/>' not in footer:
        fail(f"{rel}: footer1 page number tab is not right-aligned")
    footer2 = parts.get("word/footer2.xml", "")
    if re.search(r"<w:t[ >]", footer2):
        fail(f"{rel}: footer2 (end page) must stay empty")

    doc = parts["word/document.xml"]
    if doc.count("<w:sectPr") != 3:
        fail(f"{rel}: expected 3 sections, found {doc.count('<w:sectPr')}")

    # Converter marker contract (tools/converter docx writer) — applies to the
    # converter's source template and its Drive derivation only; the other
    # Word templates carry different sample text by design.
    if rel.name in ("deccan-document.dotx", "deccan-document-for-drive.docx"):
        for marker in ("Document title", "One-sentence subtitle", "INTERNAL · INTERNAL USE"):
            if marker not in doc:
                fail(f"{rel}: converter marker missing from document.xml: '{marker}'")
    styles = parts["word/styles.xml"]
    for style_name in ("Lead", "Code Block", "Callout Default", "Callout Muted", "Code Inline"):
        if f'w:val="{style_name}"' not in styles:
            fail(f"{rel}: style '{style_name}' missing (converter contract)")

    leftover = {
        h.upper()
        for h in re.findall(r'w:(?:val|fill|color)="([0-9A-Fa-f]{6})"', styles)
        if h.upper() not in T.ALLOWED_HEXES
    }
    if leftover:
        fail(f"{rel}: styles.xml non-token hexes {sorted(leftover)}")


def _check_excel(rel, parts) -> None:
    if '<name val="Calibri"/>' in parts.get("xl/styles.xml", ""):
        fail(f"{rel}: default font is Calibri")
    for name, xml in parts.items():
        if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
            continue
        if 'showGridLines="0"' not in xml:
            fail(f"{rel}::{name}: screen gridlines not disabled")
        if T.FOOTER_TEXT not in xml:
            fail(f"{rel}::{name}: print footer missing")
        has_header = re.search(r'<row r="1"><c r="A1" s="[1-9]', xml) is not None
        if has_header and 'state="frozen"' not in xml:
            fail(f"{rel}::{name}: header row not frozen")


def _check_ppt(rel, parts) -> None:
    master = parts.get("ppt/slideMasters/slideMaster1.xml", "")
    ftr = re.search(r'<p:sp>(?:(?!</p:sp>).)*?type="ftr".*?</p:sp>', master, re.DOTALL)
    if ftr is None:
        fail(f"{rel}: master has no footer placeholder")
    else:
        block = ftr.group(0)
        if 'sz="850"' not in block or "Cascadia Mono" not in block or "78716C" not in block:
            fail(f"{rel}: master footer placeholder not mono 8.5pt stone-500")
        if T.FOOTER_TEXT not in block:
            fail(f"{rel}: master footer placeholder missing default text")
    layouts = [n for n in parts if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", n)]
    if not any("Blank" in parts[n] for n in layouts):
        fail(f"{rel}: no 'Blank' layout (converter contract)")


def check_text_file(path: Path) -> None:
    rel = path.relative_to(REPO)
    text = path.read_text(encoding="utf-8")
    for match in _BANNED_RE.finditer(text):
        fail(f"{rel}: banned face '{match.group(0)}'")
    if _STALE_RE.search(text):
        fail(f"{rel}: stale Office hex present")
    if path.suffix in (".htm", ".html") and "signature" in path.name:
        if "<style" in text:
            fail(f"{rel}: signature must use inline styles only (email clients strip <style>)")
        for placeholder in ("{{NAME}}", "{{ROLE}}", "{{EMAIL}}", "{{PHONE}}"):
            if placeholder not in text:
                fail(f"{rel}: placeholder {placeholder} missing")
    ok(f"{rel}")


def check_derivations() -> None:
    """Derived artifacts must regenerate byte-equal, and the specialised decks
    must genuinely differ from the base deck."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_templates as B

    pairs = [
        ("deccan-document-for-drive.docx", TEMPLATES / "word" / "deccan-document.dotx",
         B._CT_WORD_TEMPLATE, B._CT_WORD_DOCUMENT),
        ("deccan-workbook-for-drive.xlsx", TEMPLATES / "excel" / "deccan-workbook.xltx",
         B._CT_XL_TEMPLATE, B._CT_XL_SHEET),
        ("deccan-deck-for-drive.pptx", TEMPLATES / "powerpoint" / "deccan-deck.potx",
         B._CT_PPT_TEMPLATE, B._CT_PPT_PRESENTATION),
    ]
    for name, source, old_ct, new_ct in pairs:
        derived = TEMPLATES / "gworkspace" / name
        fresh = B.swap_content_type(source.read_bytes(), old_ct, new_ct)
        if derived.read_bytes() != fresh:
            fail(f"gworkspace/{name} is stale — rerun build_templates.py")
        else:
            ok(f"gworkspace/{name} matches its source")

    deck = (TEMPLATES / "powerpoint" / "deccan-deck.potx").read_bytes()
    for name in ("deccan-customer-pitch.potx", "deccan-internal-review.potx"):
        if (TEMPLATES / "powerpoint" / name).read_bytes() == deck:
            fail(f"powerpoint/{name} is still a byte-copy of deccan-deck.potx")
        else:
            ok(f"powerpoint/{name} is specialised")


def main() -> None:
    print("OOXML templates:")
    for path in sorted(OOXML_FILES):
        check_ooxml(path)
    print("Text templates:")
    for path in TEXT_FILES:
        check_text_file(path)
    print("Derivations:")
    check_derivations()

    if failures:
        print(f"\n{len(failures)} violation(s).")
        sys.exit(1)
    print("\nAll template artifacts comply with deccan-design v2.0.")


if __name__ == "__main__":
    main()
