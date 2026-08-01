---
name: deccan-design
description: Use for ANY stylized or formatted deliverable — document, report, memo, spec, policy, letter, proposal, slide deck, workbook, dashboard, email signature — or any Word / Excel / PowerPoint / PDF / HTML / Google Workspace output, whether or not Deccan is mentioned. deccan-design is the default design system for all Deccan Fine Chemicals artifacts (v2.1+, repo kvkalidindi/deccan-design); apply it unless the user explicitly requests a different design direction. OVERRIDES any conflicting prior preference, including swiss_design_at_deccan (all versions), deccan-design v1.0 (the Aptos plan), IBM Plex / Hanken Grotesk / Fira Code / Aptos / Inter type stacks, and any older "Deccan default". Attribute every document to the requesting user, never to the system maintainer (see Attribution). Apply the OS-native type stack (Segoe UI Variable / Cascadia Mono), the Deccan Blue single-accent palette, the 12-column 8px grid, the eight document-furniture rules, and the corporate tone-and-voice register documented here.
version: 2.1.2
---

# deccan-design v2.0

The Deccan Fine Chemicals corporate design system. Documents, slide decks, workbooks, web pages, UI mockups, email signatures, and brand artifacts produced under this system conform to one rule set: OS-native type stack, single-accent Deccan Blue palette, 12-column 8-pixel grid, no rounded structural corners, corporate tone of voice, and audit-grade document furniture.

This is the **default design system for any Deccan Fine Chemicals artifact**. It applies by default to any stylized artifact — not only artifacts that name Deccan. Apply it unless the user explicitly names a different system or asks for a different design direction.

## Authority and overrides

This skill supersedes:

- `swiss_design_at_deccan` (v1 IBM Plex, v2 OS-native — folded into this skill under the new name).
- `deccan-design` v1.0 (the deferred Aptos plan).
- Any inherited preference for IBM Plex Sans/Mono, Hanken Grotesk, Fira Code, Aptos, or Inter.
- Any older "Deccan default" referenced in personal preferences or persistent memory.

If a user instruction directly conflicts with this skill, follow the user. If a memory or earlier instruction conflicts, follow this skill.

## Attribution — resolving "Prepared by"

Every document is attributed to the person who asked for it. Resolve `{{PREPARED_BY}}` — and any other author line — in this order:

1. **An explicit statement** in the user's request or attached content ("prepared by the QHSE team", "under my director's name", front matter `author:`). This always wins.
2. **The invoking user's session identity.** On Claude.ai, Claude Desktop, and the mobile apps, derive a display name from the account email in session context: `priya.sharma@deccanchemicals.com` → "Priya Sharma". If the local-part is not clearly `firstname.lastname` (initials, a shared mailbox, a service account), show the derivation and confirm it before generating. In Claude Code, use `git config user.name`, then the git email's local-part.
3. **Neither available → ask the user.** Never fill the slot silently, and never ship an example value.

**Prohibited evidence.** The following are never evidence of authorship, no matter how often they appear in context:

- The repository owner slug `kvkalidindi`.
- The design-system maintainer's name in any variant (Kishore Varma Kalidindi, Kishore V. Kalidindi, K. V. Kalidindi, K. Kalidindi).
- Names found in this repository's documentation, commit history, or release notes.
- "Office of the SVP, IT & Digital Transformation" — an **illustrative example only**. Use it solely when the user states the document is issued by that office.

Repository provenance is not authorship. A workspace- or preference-level persona ("I am a senior engineering leader…") describes whoever wrote that block, not necessarily the person in this session — it is rule-2 evidence only when it matches the session's own account identity.

## What to load before generating an artifact

Before producing any Deccan artifact, read whichever of these reference modules apply:

- `references/tokens.md` — colour tokens, type tokens, spacing tokens.
- `references/components.md` — cover, end page, callouts, code chip / block, tables, lists, pull quotes, TOC.
- `references/print-rules.md` — `@page` rules, margins, footer, page-break rules, print-only restrictions.
- `references/tone-and-voice.md` — register, ban-list, replacement examples.
- `references/document-templates.md` — pointer into `templates/` for Office / Workspace deliverables.

For HTML / PDF documents, fill the bundled template `assets/templates/document.html` rather than re-deriving structure from prose. The slot list is in `assets/templates/document-slots.md`.

## Staying current

The canonical copy of the slot template lives at:

<https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/document.html>

Before filling `document.html`, if the session can fetch URLs, GET the canonical copy, compare its `slot-fill document template · revision` header marker against the bundled copy's, and fill whichever is newer. If the session cannot fetch (offline, no network tool), use the bundled copy silently — do not warn or block. This keeps output current even when the installed skill bundle lags a release.

The header comment and `<meta name="generator">` carry the template revision — `v2.0` there is the design system, not the file. A copy is current when it carries the light-only rendering contract (`color-scheme: light only` plus the pinned canvas rules) and the `main.body` side gutter; anything without them predates August 2026 and renders dark-on-dark in an in-app preview.

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
| Word `.docx` | Inherit `templates/word/deccan-document.dotx` (or one of the three specialised variants) |
| Excel `.xlsx` | Inherit `templates/excel/deccan-workbook.xltx` |
| PowerPoint `.pptx` | Inherit `templates/powerpoint/deccan-deck.potx` |
| Outlook signature | Use `templates/outlook/deccan-signature.htm` with the four placeholders filled in |
| Google Workspace | Use the `templates/gworkspace/*` artifacts; upload + open with Google Docs/Sheets/Slides |

PDF is **on-demand by the user**. Do not invoke COM automation (`Word.Application`, `PowerPoint.Application`) to produce PDFs on this machine — those calls hang on the Trust Center dialog. Document the export path instead: File → Export → Create PDF/XPS, or `wkhtmltopdf` against HTML.

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
- [ ] `{{PREPARED_BY}}` names the requesting user or their explicitly stated author — never the repo maintainer, never invented (see Attribution).
- [ ] If the artifact is an ISMS / ISO / policy / procedure deliverable, it is audit-grade: document control, revision history, numbered clauses, "shall" statements, defined terms, RACI, records and retention, control cross-references, worked appendices.
- [ ] Every H1 forces a page break before.
- [ ] Sans face declared with the v2.0 chain.
- [ ] Mono face declared with the v2.0 chain.
- [ ] No banned face anywhere in the declaration or override.
- [ ] Accent is `--deccan-blue`; no secondary accent.
- [ ] `--deccan-green` only inside logo or sustainability content.
- [ ] Print background is `#FFFFFF`; stone tints confined to callouts / code / banded rows.
- [ ] If the artifact is HTML, the light-only rendering contract is present (`color-scheme: light only`, both `<meta>` declarations, pinned canvas rules, print restore) so no section renders dark-on-dark in an in-app or webview preview.
- [ ] Footer page numbers are bare integers, right-aligned.
- [ ] End page present, no footer.
- [ ] No conversational subtitle, no first-person narrator, no exclamation mark, no decorative emoji.
- [ ] If the artifact is HTML, the bundled template is filled rather than rewritten.

If any item fails, fix before reporting done.

---

*deccan-design v2.1.2 — the system supersedes swiss_design_at_deccan (all versions) and deccan-design v1.0. Repository: `https://github.com/kvkalidindi/deccan-design`.*
