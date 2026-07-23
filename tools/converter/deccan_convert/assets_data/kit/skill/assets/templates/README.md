# HTML template — usage

`document.html` is the canonical HTML / PDF document template for deccan-design v2.0.

## Quick start

```python
import pathlib

template = pathlib.Path("document.html").read_text(encoding="utf-8")

slots = {
    "TITLE": "Q2 R&D update",
    "SUBTITLE": "Process intensification programme — pilot results",
    "DOCUMENT_TYPE": "Report",
    "PREPARED_BY": "Engineering & R&D",
    "DATE": "May 2026",
    "VERSION": "1.0",
    "CLASSIFICATION": "Confidential",
    "BODY_HTML": open("body.html").read(),
}

for k, v in slots.items():
    template = template.replace(f"{{{{{k}}}}}", v)

pathlib.Path("q2-rd-update.html").write_text(template, encoding="utf-8")
```

The slot list lives in `document-slots.md`.

## What this template gives you

- The deccan-design v2.0 colour and type tokens, declared once at the top.
- Cover, body, and end-page structure that conforms to the eight document-furniture rules.
- `@page` print rules for Letter (and A4 by extension).
- All component CSS — headings, body, lists, tables, callouts, code, pull quotes, TOC.

You write the body; the template handles the rest.

## What this template does not do

- It does not fetch the logo. The cover uses a typographic wordmark (3-px Deccan Blue rule + "Deccan Fine Chemicals" in semibold). If a raster logo is needed, use `assets/logo.png` or the base64 in `assets/logo.b64.txt` and embed inline.
- It does not generate a PDF. PDF production is on-demand — open the produced HTML in a browser and print to PDF, or use `wkhtmltopdf`.
- It does not embed font binaries. The OS-native chain is the policy.

## Multiple sections

Repeat the `<section class="section">` block in `{{BODY_HTML}}`. Each `<h1>` forces a page break before. The first body H1 does not page-break (the cover already broke).

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
