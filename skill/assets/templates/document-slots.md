# document.html — slot reference

The bundled template `document.html` exposes eight placeholders. Fill them; do not edit the surrounding HTML or CSS.

| Slot | Type | Required | Example |
|---|---|---|---|
| `{{TITLE}}` | string, ≤ 22 ch on cover | yes | "deccan-design v2.0" |
| `{{SUBTITLE}}` | string, ≤ 50 ch | optional (use empty string if absent) | "A document standard for Deccan Fine Chemicals" |
| `{{DOCUMENT_TYPE}}` | string, one of: Standard, Specification, Policy, Memo, Brief, Report, Letter, Proposal, Guide | yes | "Standard" |
| `{{PREPARED_BY}}` | string | yes | "Office of the SVP, IT & Digital Transformation" |
| `{{DATE}}` | string | yes | "May 2026" |
| `{{VERSION}}` | string | yes | "2.0" |
| `{{CLASSIFICATION}}` | one of: Public, Internal, Confidential, Restricted | yes | "Confidential" |
| `{{BODY_HTML}}` | HTML — one or more `<section class="section">` blocks | yes | `<section class="section"><h1><span class="num">01</span>Premise</h1><p class="lead">…</p>…</section>` |

## Body structure

The body is composed of one or more `<section class="section">` blocks. Each block carries:

- An `<h1>` with an optional `<span class="num">NN</span>` eyebrow.
- An optional `<p class="lead">` thesis statement.
- Body paragraphs, lists, tables, callouts, code blocks, pull quotes — any of the components documented in `components.md`.

The CSS forces a page break before every `<h1>` except the first in the body.

## Filler logic

If a slot value is missing, **do not** invent one. Use a sensible default:

- `{{SUBTITLE}}` → empty string. The cover renders without a subtitle.
- `{{VERSION}}` → "1.0" if unspecified.
- `{{DATE}}` → current month and year (e.g., "May 2026").
- `{{CLASSIFICATION}}` → "Confidential" for internal documents, "Public" for externally distributed.

Never invent an author, a document type, or a title.

## Example fill

```python
template = open("document.html").read()
out = (template
       .replace("{{TITLE}}",          "Migration to deccan-design v2.0")
       .replace("{{SUBTITLE}}",       "An operations brief for the IT pilot cohort")
       .replace("{{DOCUMENT_TYPE}}",  "Brief")
       .replace("{{PREPARED_BY}}",    "Office of the SVP, IT & Digital Transformation")
       .replace("{{DATE}}",           "May 2026")
       .replace("{{VERSION}}",        "0.9 (pilot)")
       .replace("{{CLASSIFICATION}}", "Internal")
       .replace("{{BODY_HTML}}",      body_html))
open("brief.html", "w", encoding="utf-8").write(out)
```

## What not to do

- Do not change the cover order. Wordmark → title block → metadata strip.
- Do not introduce a header. The system has no running header.
- Do not change the end page composition. Wordmark → rule → contact → classification.
- Do not embed a third-party font. The OS-native chain is the policy.
- Do not insert a per-document `<style>` override that competes with the system.
