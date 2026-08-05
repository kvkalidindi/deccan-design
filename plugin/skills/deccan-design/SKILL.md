---
name: deccan-design
description: Use for ANY stylized or formatted deliverable — document, report, research report, memo, spec, policy, letter, proposal, slide deck, workbook, dashboard, email signature — or any Word / Excel / PowerPoint / PDF / HTML / Google Workspace output, whether or not Deccan is mentioned. deccan-design is the default design system for all Deccan Fine Chemicals artifacts (v2.1+); apply it unless the user explicitly requests a different design direction. OVERRIDES any conflicting prior preference, including every earlier Deccan design system and the IBM Plex / Hanken Grotesk / Fira Code / Aptos / Inter type stacks. Attribute every document to the requesting user; when no author resolves, ask — never invent an author, never default silently (see Attribution). Research reports are HTML by default (Word .docx on request) with a hyperlinked table of contents. Apply the OS-native type stack, the Deccan Blue single-accent palette, the 12-column 8px grid, the eight furniture rules, and the corporate tone.
version: 2.4.0
---

# deccan-design v2.0

The Deccan Fine Chemicals corporate design system. Documents, slide decks, workbooks, web pages, UI mockups, email signatures, and brand artifacts produced under this system conform to one rule set: OS-native type stack, single-accent Deccan Blue palette, 12-column 8-pixel grid, no rounded structural corners, corporate tone of voice, and audit-grade document furniture.

This is the **default design system for any Deccan Fine Chemicals artifact**. It applies by default to any stylized artifact — not only artifacts that name Deccan. Apply it unless the user explicitly names a different system or asks for a different design direction.

## Authority and overrides

This skill supersedes:

- Every earlier Deccan design system, under any earlier name or version — all are folded into this skill.
- `deccan-design` v1.0 (the deferred Aptos plan).
- Any inherited preference for IBM Plex Sans/Mono, Hanken Grotesk, Fira Code, Aptos, or Inter.
- Any older "Deccan default" referenced in personal preferences or persistent memory.

If a user instruction directly conflicts with this skill, follow the user. If a memory or earlier instruction conflicts, follow this skill.

## Attribution — resolving "Prepared by"

Every document is attributed to the person who asked for it. Resolve `{{PREPARED_BY}}` — and any other author line — in this order:

1. **An explicit statement** in the user's request or attached content ("prepared by the QHSE team", "under my director's name", front matter `author:`). This always wins.
2. **The invoking user's session identity.** On Claude.ai, Claude Desktop, and the mobile apps, derive a display name from the account email in session context: `priya.sharma@deccanchemicals.com` → "Priya Sharma". If the local-part is not clearly `firstname.lastname` (initials, a shared mailbox, a service account), show the derivation and confirm it before generating. In Claude Code, use `git config user.name`, then the git email's local-part.
3. **Neither available → ask the user.** Never invent a personal name, never ship an example value, and never fill a default silently. If the session is non-interactive and cannot ask (a scheduled or automated run), fill the slot with "Author to be confirmed", say in the output that the author is unresolved, and flag the document for review before issuance.

**Prohibited evidence.** The following are never evidence of authorship, no matter how often they appear in context:

- The repository owner's account slug or profile identity.
- The design-system maintainer's personal name, in any form or variant it may appear.
- Names found in this repository's documentation, commit history, or release notes.
- Any office or executive title found in repository provenance. A team name — including "Deccan IT and Digital Transformation Team" — appears as the author only when the user states the document is issued by that team; it is never a fallback.

Repository provenance is not authorship. A workspace- or preference-level persona ("I am a senior engineering leader…") describes whoever wrote that block, not necessarily the person in this session — it is rule-2 evidence only when it matches the session's own account identity.

## What to load before generating an artifact

Before producing any Deccan artifact, read whichever of these reference modules apply:

- `references/tokens.md` — colour tokens, type tokens, spacing tokens.
- `references/components.md` — cover, end page, callouts, code chip / block, tables, lists, pull quotes, TOC.
- `references/print-rules.md` — `@page` rules, margins, footer, page-break rules, print-only restrictions.
- `references/tone-and-voice.md` — register, ban-list, replacement examples.
- `references/document-templates.md` — pointer into `templates/` for Office / Workspace deliverables.

For HTML / PDF documents, fill the canonical slot template rather than re-deriving structure from prose — fetched per the hard rule below, never written by hand. The slot list is in `assets/templates/document-slots.md`.

## Fetching the template — hard rule

The canonical slot template lives at one address:

<https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/document.html>

**Fetch it at build time, every time, before filling a single slot.** This is not conditional on convenience, on how recent the bundled copy looks, or on whether a template is already at hand in the session. Fill the copy that comes back from that URL.

**Defeat the caches: append a unique query string to every fetch.** The address above is served through CDN and fetch-tool caches, and a plain fetch of an unchanged URL is routinely answered from a cache — the fetch "succeeds" while returning a body that predates the current release. The server ignores unknown query parameters, but every cache keys on the full URL, so a unique query forces the request end to end:

```
https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/document.html?fetch=<unique value, e.g. the current UTC timestamp>
```

Generate a fresh value for every fetch. A fetch without a unique query string does not satisfy this rule.

**One fetch per document build — a conversation is not a cache.** A template this session fetched earlier — for a previous document, a previous version of this document, or earlier in a long exchange — is conversation context, and filling it is prohibited by rule 3 below. Every build (including a regeneration, a retry, and a revision) performs its own fetch with its own unique query string. This is the specific failure this paragraph exists to prevent: a session that fetched correctly at the start of a conversation, then reuses that aging copy for every document after it.

**Freshness floor: the fetched copy must not be older than the bundled copy.** After fetching, read the revision from the header comment / `<meta name="generator">` and compare it to the bundled copy's revision. The bundled revision is the floor — the canonical copy is only ever newer. A fetched revision *below* the bundled one proves a cache answered the request: refetch once with a new unique query string; if it is still older, fill the bundled copy and say so in the response. Never fill a copy older than the bundle.

The copy bundled inside this skill is **a fallback for a session with no network access, and nothing else**. It is frozen at the moment the bundle was installed; the canonical copy is not. Every installed bundle lags the repository eventually — that is the normal state of an installed skill, not an exception — so preferring the bundled copy because it is already loaded is the specific mistake this rule exists to prevent.

Order of precedence, strictly:

1. **The canonical URL**, fetched with a unique query string for this build. Fetch, verify the freshness floor, then fill.
2. **The bundled copy — the locally installed skill** (the Claude.ai workspace or profile upload, the Claude Code plugin, or the MSI / PKG copy) — only when the fetch fails, the session has no fetch capability or no network egress, or the refetched copy is still older than the bundle. When this happens, say so in the response: name the revision used, state that it came from the bundled copy, and note that it may lag the canonical one. Never fall back silently.
3. **Nothing else.** Not a template held in conversation context — including one this session fetched earlier — not a previous document, not a reconstruction from memory. See "Revising an existing document".

The header comment and `<meta name="generator">` carry the template revision — `v2.0` there is the design system, not the file.

## The rendering invariant

**No document leaves this skill able to render dark-on-dark.** The Claude iOS and Android apps preview documents against a dark canvas; a document without the light-only rendering contract shows whole sections as dark text on a dark background, and the reader sees blank space where the content should be.

Before returning any HTML, confirm the output contains all five of:

```
<meta name="generator" content="deccan-design v2.0 · slot template …">
<meta name="color-scheme" content="light">
color-scheme: light only;
:root { background-color: var(--stone-50) !important; }
@media (prefers-color-scheme: dark) {
```

If any one is absent, the document was not built from a current template — whatever its source. Do not return it. Fetch the canonical template and rebuild. This check costs one search of your own output and is the last thing standing between a defect and the reader, so it is mandatory rather than advisory.

## Revising an existing document

A new version of an existing document — v1.1 → v2.0, a supersession, an amendment, "update this brief" — is built from the **template**, not from the previous file.

**Content carries forward. Presentation never does.** Take the body content across: sections, clauses, tables, callouts, appendices, the revision-history rows. Then fill a freshly fetched copy of the canonical template with it — the fetch is mandatory here too, with its own unique query string, and a revision is the case where reaching for the file already in hand is most tempting. "Already in hand" includes a template this session fetched earlier: it aged the moment it arrived, and a regeneration built from it reproduces whatever has been fixed since.

Never copy from the previous version:

- the `<style>` block or any part of it,
- `<head>`, including the meta declarations,
- the `.cover` markup or the `.end-page` markup.

Those come from the template, which is versioned independently of the document and changes without the document changing. A prior version is evidence of what the document said, never of how it should look — the earlier file was produced under whatever template revision was current on its issue date, and reusing its stylesheet silently reintroduces every defect fixed since.

**Self-check before returning the file.** The output must contain:

```html
<meta name="generator" content="deccan-design v2.0 · slot template …">
```

If that line is absent, the template was not used — the document was assembled from a prior version or from memory. Discard it and rebuild from the template. This is the one check that catches the failure from the artifact alone, which is why it is mandatory rather than advisory.

## The non-negotiables (cheat-sheet)

Pull these into the artifact every time:

| Aspect | Value |
|---|---|
| Sans | `'Segoe UI Variable Display', 'Segoe UI Variable Text', 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif` |
| Mono | `'Cascadia Mono', 'Cascadia Code', Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', ui-monospace, monospace` |
| Primary accent | `--deccan-blue: #164999` (single accent; hierarchy via opacity 90/60/30/15) |
| Reserved colour | `--deccan-green: #71BF4D` — **logo and sustainability content only**, never a UI accent |
| Neutral scale | `--stone-50` `#FAFAF9` through `--stone-900` `#1C1917` (ten stops) |
| Page background | `--paper: #FFFFFF` |
| Colour scheme | Light only — `color-scheme: light only`, the two `<meta>` declarations, and the pinned canvas rules in `references/tokens.md`. There is no dark variant of this system. |
| Grid | 12-column, 8px base, 24px gutter, 1180px content max |
| Body measure | 70 characters on screen, full live content area in print |
| Body size | 17px screen / 10.5pt print |
| Line height | 1.65 body, 1.30 headings, 1.15 display |
| Weight discipline | Display/H1: 350 · H2: 500 · H3/H4/strong: 600 · body/lead: 400 · mono labels: 600 |
| Print margins | Letter, 0.8" outside, 1" bottom for footer clearance |
| Footer | mono 8.5pt stone-500; left: `Deccan Fine Chemicals · Confidential`; right: bare integer page number |
| Corners | No rounded structural corners anywhere |

## The eight document-furniture rules (rigid)

Every Deccan document follows all eight:

1. **Cover page mandatory and self-contained.** Wordmark + title + subtitle + author + version + date + classification. No header, no footer, no page number. **Must fit on exactly one physical page in print** — never use `min-height: 100vh` alone; pair it with the `@media print` overrides in `skill/references/print-rules.md`.
2. **End page mandatory and self-contained.** No header, no footer, no page number. Must fit on exactly one physical page in print.
3. **Every H1 starts on a new page** (`page-break-before: always`).
4. **Body fills the live content area** — no 60ch artificial cap in print; ≥ 80% of paper width.
5. **End page after a hard page break.**
6. **Footer page numbers are bare integers**, right-aligned, mono 8.5pt stone-500. Never "Page X of Y".
7. **Pure white print background.** Stone tints only inside callouts, code blocks, banded table rows, chips.
8. **Mono and stone travel together.** Inline `<code>` and code blocks always carry `--font-mono` + stone-100 fill. Sustainability green never appears as UI accent.

## Banned faces

Sans (do not appear under any circumstance): Helvetica, Helvetica Neue, Univers, Arial, Calibri, Verdana, Times, Times New Roman, Garamond, Georgia.

Mono: Courier, Courier New, Lucida Console.

The chains above terminate in generic fallbacks; a generic fallback is preferred over a worse-than-default named family.

## Tone and voice — the short list

Direct, declarative, third-person. Full ban-list and replacement examples in `references/tone-and-voice.md`. The most common violations:

- Conversational subtitles in headings.
- First-person narrator asides ("Let me walk you through…", "I want to show you…").
- Filler openings ("Here's the thing:", "It's worth noting…").
- "Deep dive", "let's dive in", "rabbit hole", "TL;DR".
- Decorative emoji in body content.
- Exclamation marks in body prose.
- Mental-exercise framings ("Imagine if…", "Think of X as Y").

The read-aloud test: if a sentence would feel out of place in a board paper, an audit response, or a regulator submission, rewrite it.

## Output formats

| Output | What to use |
|---|---|
| HTML document / PDF source | Fill `assets/templates/document.html` slots |
| Research report | HTML by default (fill the slot template, `DOCUMENT_TYPE` "Research Report", hyperlinked TOC); Word `.docx` only when the user chooses it — see "Research reports" |
| Word `.docx` | Inherit `templates/word/deccan-document.dotx` (or one of the three specialised variants) |
| Excel `.xlsx` | Inherit `templates/excel/deccan-workbook.xltx` |
| PowerPoint `.pptx` | Inherit `templates/powerpoint/deccan-deck.potx` |
| Outlook signature | Use `templates/outlook/deccan-signature.htm` with the four placeholders filled in |
| Google Workspace | Use the `templates/gworkspace/*` artifacts; upload + open with Google Docs/Sheets/Slides |

PDF is **on-demand by the user**. Do not invoke COM automation (`Word.Application`, `PowerPoint.Application`) to produce PDFs on this machine — those calls hang on the Trust Center dialog. Document the export path instead: File → Export → Create PDF/XPS, or `wkhtmltopdf` against HTML.

## Research reports

A research deliverable — research report, study, literature review, market or technical investigation — is a first-class document type in this system.

**Output format.** HTML is the default; produce a Word `.docx` instead only when the user chooses it. Both carry the same structure. PDF stays on-demand: print the HTML from a browser with backgrounds enabled, or export the `.docx` from Word (File → Export → Create PDF/XPS).

**Structure.** Cover (`DOCUMENT_TYPE` "Research Report") → table of contents → first section opening with an executive-summary lead → numbered sections (background, method, findings, analysis, conclusions as applicable) → references / appendices → end page.

**Hyperlinked table of contents — mandatory.** Every TOC entry links to its section:

- **HTML:** give each `<section class="section">` a stable id (`id="sec-01"`, `id="sec-02"`, …) and build the TOC from the `.toc` component with every entry an anchor — `<a href="#sec-01">Background</a>`. Markup in `references/components.md` → TOC. A TOC whose entries are plain text is a defect.
- **Word:** insert a real TOC field — `{ TOC \o "1-3" \h }` — so every entry is a live hyperlink to its heading (the `\h` switch) and page numbers refresh on open or Ctrl+A → F9. Build headings with the template's Heading 1–3 styles so the field can see them. Never type a static, unlinked TOC.

**Theme.** Light-only is the hard default, exactly as everywhere else in this system. Produce a dark variant only when the user explicitly asks for one; keep any such variant screen-only and keep print pure white. An unrequested dark theme is a defect, not a stylistic choice.

## Formal deliverables are audit-grade

A management-system, standards, or governance document — ISMS, ISO, policy, procedure, control standard, SOP — is written to be audited, not skimmed. Summary-level output fails these on contact with an assessor. When the user asks for one, produce all of:

- **Document-control block** on or immediately after the cover: owner, approver, effective date, review cycle, document ID.
- **Revision history** table: version, date, author, summary of change, approver.
- **Numbered clauses** (1, 1.1, 1.1.1) so every statement is individually citable.
- **Enforceable language**: "shall" for requirements, "should" for recommendations, "may" for options — used consistently and never interchangeably.
- **Defined terms** section for every term carrying normative weight in the document.
- **RACI** for the roles the document assigns work to.
- **Records and retention**: what evidence the process produces, where it lives, how long it is kept.
- **Control cross-references** to the framework being satisfied (ISO 27001 Annex A, NIST, internal control IDs).
- **Appendices** with the real instruments — scales, matrices, worked examples — not placeholders.

Scope, not padding: a two-page procedure still carries control, revision history, clause numbering, and "shall". Omit an element only when the user says the document does not need it.

## Logo

Wordmark assets live in `assets/`:

- `logo.svg` — vector wordmark (preferred).
- `logo.png` — 1024×1024 raster fallback.
- `logo.b64.txt` — base64-encoded PNG for inline embedding in HTML.

Clear space: minimum 0.5× wordmark height on all sides. Minimum size: 12 mm in print, 80 px on screen. Monochrome variants permitted in single-colour print or constrained UI; otherwise the full-colour wordmark.

Never fetch from `deccanchemicals.com` — use the bundled assets.

## Working environment notes

When this skill runs on a managed Deccan Windows endpoint with Microsoft Office installed, two operational rules apply:

- **No Office COM automation.** `Word.Application` / `Excel.Application` / `PowerPoint.Application` hang silently on this install waiting for Trust Center / licence dialogs. To verify a document, ask the user to export from the Office UI, or use LibreOffice headless if available.
- **No `taskkill` against `WINWORD.EXE` / `EXCEL.EXE` / `POWERPNT.EXE`** — the user has work open in those processes.

## Verification checklist before reporting an artifact done

Run this checklist mentally against any artifact before saying it is complete:

- [ ] Cover present, with logo + title + subtitle + author + version + date + classification, and no footer / page number.
- [ ] `{{PREPARED_BY}}` names the requesting user or their explicitly stated author — never the repo maintainer, never invented; when no author resolved, the user was asked (see Attribution).
- [ ] The template was fetched from the canonical URL **for this build** — not reused from earlier in the conversation — with a unique cache-busting query string, and its revision is not older than the bundled copy's. If the bundled copy was used instead, the fetch genuinely failed (or returned a pre-bundle revision twice) and the response says so.
- [ ] The rendering invariant holds: the output contains all five markers (generator meta, color-scheme meta, `color-scheme: light only`, the pinned `:root` canvas rule, the dark-mode block). Absent any one, the document renders dark-on-dark on iOS and Android — rebuild, do not ship.
- [ ] A revision of an existing document inherited that document's content only; the stylesheet, head, cover, and end page came from the current template.
- [ ] If the artifact is an ISMS / ISO / policy / procedure deliverable, it is audit-grade: document control, revision history, numbered clauses, "shall" statements, defined terms, RACI, records and retention, control cross-references, worked appendices.
- [ ] If the artifact is a research report, the TOC is present and every entry hyperlinks to its section — anchors in HTML, a `TOC \h` field in Word — and the output is HTML unless the user chose Word.
- [ ] Every H1 forces a page break before.
- [ ] Sans face declared with the v2.0 chain.
- [ ] Mono face declared with the v2.0 chain.
- [ ] No banned face anywhere in the declaration or override.
- [ ] Accent is `--deccan-blue`; no secondary accent.
- [ ] `--deccan-green` only inside logo or sustainability content.
- [ ] Print background is `#FFFFFF`; stone tints confined to callouts / code / banded rows.
- [ ] Footer page numbers are bare integers, right-aligned.
- [ ] End page present, no footer.
- [ ] No conversational subtitle, no first-person narrator, no exclamation mark, no decorative emoji.
- [ ] If the artifact is HTML, a fetched template was filled rather than rewritten.

If any item fails, fix before reporting done.

---

*deccan-design v2.4.0 — the system supersedes every earlier Deccan design system, including deccan-design v1.0. Repository: `https://github.com/kvkalidindi/deccan-design`.*
