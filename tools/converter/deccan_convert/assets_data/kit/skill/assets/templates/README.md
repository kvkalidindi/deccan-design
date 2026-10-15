# HTML templates — usage

Two canonical HTML / PDF document templates, one per tier (`SKILL.md` → "Document tiers"):

- `document-compact.html` — **the default**. Slim title block on page one: title, then `Version · Date`. No author line, cover, end page, or audit furniture.
- `document.html` — **formal tier**: the user calls the document a report or a formal document, names a formal element, or asks for an audit-grade type. Cover with author, version and date; document-control page with the revision history; end page.

Fetch the tier's template from its canonical URL for every build (`SKILL.md` → "Fetching the template — hard rule"); the copies here are the no-network fallback.

## Quick start — compact (default)

```python
import pathlib

template = pathlib.Path("document-compact.html").read_text(encoding="utf-8")

slots = {
    "TITLE": "Python 3.13 pilot rollout",
    "SUBTITLE": "",
    "VERSION": "1.0",
    "DATE": "May 2026",
    "BODY_HTML": open("body.html").read(),
}

for k, v in slots.items():
    template = template.replace(f"{{{{{k}}}}}", v)

pathlib.Path("pilot-rollout.html").write_text(template, encoding="utf-8")
```

## Quick start — formal

```python
template = pathlib.Path("document.html").read_text(encoding="utf-8")

slots = {
    "TITLE": "Q2 R&D update",
    "SUBTITLE": "Process intensification programme — pilot results",
    "DOCUMENT_TYPE": "Report",
    "PREPARED_BY": prepared_by,  # resolved per SKILL.md -> Attribution: stated author, else the requesting user, else ask
    "DATE": "May 2026",
    "VERSION": "1.0",
    "CLASSIFICATION": "Confidential",
    "DOCUMENT_ID": "Not assigned",
    "OWNER": prepared_by,
    "APPROVER": "Pending approval",
    "EFFECTIVE_DATE": "May 2026",
    "REVIEW_CYCLE": "Not set",
    "REVISION_ROWS": f"<tr><td>1.0</td><td>May 2026</td><td>{prepared_by}</td><td>Initial issue</td><td>Pending approval</td></tr>",
    "BODY_HTML": open("body.html").read(),
}

for k, v in slots.items():
    template = template.replace(f"{{{{{k}}}}}", v)

pathlib.Path("q2-rd-update.html").write_text(template, encoding="utf-8")
```

The slot list lives in `document-slots.md`.

## What this template gives you

- The deccan-design v2.0 colour and type tokens, declared once at the top.
- Compact: the title block and body. Formal: cover, document-control page, body, and end page, conforming to the eight document-furniture rules.
- `@page` print rules for Letter (and A4 by extension).
- The light-only rendering contract (`references/tokens.md`), so the document previews light-on-white inside hosts that theme their content area dark — the Claude iOS in-app viewer, chat and mail webviews — instead of rendering dark stone text on a dark canvas.
- All component CSS — headings, body, lists, tables, callouts, code, pull quotes, TOC.

You write the body; the template handles the rest.

## What this template does not do

- It does not fetch the logo. The cover uses a typographic wordmark (3-px Deccan Blue rule + "Deccan Fine Chemicals" in semibold). If a raster logo is needed, use `assets/logo.png` or the base64 in `assets/logo.b64.txt` and embed inline.
- It does not generate a PDF. PDF production is on-demand — open the produced HTML in a browser and print to PDF, or use `wkhtmltopdf`.
- It does not embed font binaries. The OS-native chain is the policy.

## Multiple sections

Repeat the `<section class="section">` block in `{{BODY_HTML}}`. In the formal template each `<h1>` forces a page break before, except the first body H1 (the document-control page already broke). The compact template flows continuously.

```html
<section class="section">
  <h1><span class="num">01</span>Background</h1>
  <p class="lead">…</p>
  <p>…</p>
</section>
<section class="section">
  <h1><span class="num">02</span>Findings</h1>
  …
</section>
```
