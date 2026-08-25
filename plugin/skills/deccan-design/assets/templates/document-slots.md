# Template slot reference — compact and formal

Two slot templates, one per document tier (`SKILL.md` → "Document tiers"):

- `document-compact.html` — **the default**. Slim title block, no cover, no end page.
- `document.html` — **formal tier only**: used when the user requests a formal document or an audit-grade type (policy, SOP, ISO/ISMS).

Fill the placeholders; do not edit the surrounding HTML or CSS.

Fill the copy fetched from the tier's canonical URL at build time — see `SKILL.md` → "Fetching the template — hard rule". Every build performs its own fetch with a unique cache-busting query string (`?fetch=<unique value>`); a copy this session fetched earlier, a copy taken from an earlier document, a fetch rendering (markdown-converted text — see the source-integrity rule), and a fetched copy whose revision is older than the bundled one are all unacceptable. The copy bundled in the skill is a no-network fallback only.

## Compact template — `document-compact.html` (default)

Five placeholders:

| Slot | Type | Required | Example |
|---|---|---|---|
| `{{TITLE}}` | string | yes | "Python 3.13 pilot rollout" |
| `{{SUBTITLE}}` | string, ≤ 60 ch | optional (use empty string if absent) | "Status memo, August 2026" |
| `{{PREPARED_BY}}` | string | yes | the requesting user's resolved display name — see PREPARED_BY resolution below; never an example or invented value |
| `{{DATE}}` | string | yes | "August 2026" |
| `{{BODY_HTML}}` | HTML — one or more `<section class="section">` blocks | yes | as below |

No document type, version, or classification slots exist in the compact template — those are formal-tier metadata. If the user states a classification or version for a compact document, carry it in the body or the subtitle where they ask for it, or offer the formal tier.

## Formal template — `document.html`

Eight placeholders:

| Slot | Type | Required | Example |
|---|---|---|---|
| `{{TITLE}}` | string, ≤ 22 ch on cover | yes | "deccan-design v2.0" |
| `{{SUBTITLE}}` | string, ≤ 50 ch | optional (use empty string if absent) | "A document standard for Deccan Fine Chemicals" |
| `{{DOCUMENT_TYPE}}` | string, one of: Standard, Specification, Policy, Memo, Brief, Report, Research Report, Letter, Proposal, Guide | yes | "Standard" |
| `{{PREPARED_BY}}` | string | yes | the requesting user's resolved display name — see PREPARED_BY resolution below; never an example or invented value |
| `{{DATE}}` | string | yes | "May 2026" |
| `{{VERSION}}` | string | yes | "2.0" |
| `{{CLASSIFICATION}}` | one of: Public, Internal, Confidential, Restricted | yes | "Confidential" |
| `{{BODY_HTML}}` | HTML — one or more `<section class="section">` blocks | yes | `<section class="section"><h1><span class="num">01</span>Premise</h1><p class="lead">…</p>…</section>` |

## Body structure

The body is composed of one or more `<section class="section">` blocks. Each block carries:

- An `<h1>` with an optional `<span class="num">NN</span>` eyebrow.
- An optional `<p class="lead">` thesis statement.
- Body paragraphs, lists, tables, callouts, code blocks, pull quotes — any of the components documented in `components.md`.

In the **formal** template the CSS forces a page break before every `<h1>` except the first in the body. The **compact** template flows continuously — no forced breaks.

For a document that carries a table of contents — mandatory for a research report in either tier — give every `<section class="section">` a stable id (`id="sec-01"`, `id="sec-02"`, …) and make every TOC entry an anchor to it: `<a href="#sec-01">Background</a>`. The TOC markup is the `.toc` component in `components.md`; a TOC whose entries are plain text is a defect. Both templates carry the `.toc` styling.

## Filler logic

If a slot value is missing, **do not** invent one. Use a sensible default:

- `{{SUBTITLE}}` → empty string. The title block or cover renders without a subtitle.
- `{{VERSION}}` (formal only) → "1.0" if unspecified.
- `{{DATE}}` → current month and year (e.g., "May 2026").
- `{{CLASSIFICATION}}` (formal only) → "Confidential" for internal documents, "Public" for externally distributed.

Never invent an author, a document type, or a title. In particular, never resolve an author from repository provenance: not the repo owner slug, not the maintainer's name, not names appearing in bundled documentation or examples.

## PREPARED_BY resolution

Resolve `{{PREPARED_BY}}` in this order (full policy: `SKILL.md` → Attribution):

1. An explicit author stated in the request or the source content.
2. The invoking user's session identity — account email on Claude.ai surfaces (`priya.sharma@…` → "Priya Sharma"; confirm derivations that are not clearly `firstname.lastname`), `git config user.name` in Claude Code.
3. Neither → ask the user. Never invent a personal name, never fill a default silently, and never resolve one from repository provenance. In a non-interactive run that cannot ask, fill "Author to be confirmed", say so in the output, and flag the document for review.

## Example fill (compact, the default)

```python
template = open("document-compact.html").read()
out = (template
       .replace("{{TITLE}}",       "Migration to deccan-design v2.0")
       .replace("{{SUBTITLE}}",    "An operations brief for the IT pilot cohort")
       .replace("{{PREPARED_BY}}", prepared_by)  # resolved per SKILL.md -> Attribution: the requesting user
       .replace("{{DATE}}",        "May 2026")
       .replace("{{BODY_HTML}}",   body_html))
open("brief.html", "w", encoding="utf-8").write(out)
```

For a formal document, fill `document.html` with the eight formal slots instead.

## What not to do

- Do not add cover, end-page, revision-history, or document-control markup to a compact document — a request for those elements makes the document formal, built on `document.html`.
- Do not change the formal cover order. Wordmark → title block → metadata strip.
- Do not introduce a header. The system has no running header.
- Do not change the end page composition. Wordmark → rule → contact → classification.
- Do not embed a third-party font. The OS-native chain is the policy.
- Do not insert a per-document `<style>` override that competes with the system.
