# Verification prompt — confirm `deccan-design` is active

A one-prompt test to confirm the workspace skill and custom instructions are active and producing v2.0-compliant output. Hand to any teammate who is not the workspace admin (so personal admin caching does not mask a misconfiguration).

## The prompt

Copy and paste the text below into a fresh Claude.ai chat. Do not modify it.

```
Generate a one-page Deccan Fine Chemicals status memo about the Python 3.13
pilot rollout. Output a complete, self-contained HTML file with all CSS
inline in <head>. Cover, body sections 01-04, end page.
```

The prompt deliberately omits all design instructions. A working setup applies the system from the workspace skill and custom instructions automatically.

## Prompt B — default application (no "Deccan" mentioned)

In a second fresh chat, run:

```
Generate a one-page status memo about the Python 3.13 pilot rollout.
Output a complete, self-contained HTML file with all CSS inline in <head>.
Cover, body sections 01-04, end page.
```

Prompt B never says "Deccan". Since v2.1 the system is the org default for any stylized document, so the output must be identical in kind to Prompt A's — same type stack, same accent, same furniture. If Prompt A passes and Prompt B produces generic styling, the workspace custom instructions (org-rollout Step 3) are missing or stale.

> Prompts A and B ask for "Cover, body sections 01-04, end page" **by name** — under the v2.5.0 tier rule that request makes them formal-tier builds on purpose, so Checks 3 and 6 stay meaningful. The compact default is tested separately by Prompt C.

## Prompt C — compact default (v2.5.0+)

In a third fresh chat, run:

```
Generate a one-page status memo about the Python 3.13 pilot rollout.
Output a complete, self-contained HTML file with all CSS inline in <head>.
```

Prompt C names no furniture and no formal type, so the output must be **compact**: a slim title block (wordmark, title, author · date), then content — evaluated by Check 7.

## The seven binary checks

Checks 1–4 run against Prompt A's or B's output; checks 5–7 have their own procedure.

Open the HTML response in **View source** or save and open in a browser, then check each item.

### Check 1 — Sans face

Search the inline CSS for `font-family`. The first family on the sans chain must be `'Segoe UI Variable Display'`.

| Result | Meaning |
|---|---|
| **Pass** | `'Segoe UI Variable Display', 'Segoe UI Variable Text', 'Segoe UI Variable', 'Segoe UI', system-ui, …` | The skill is active. |
| **Fail** | `IBM Plex Sans`, `Hanken Grotesk`, `Aptos`, `Inter`, `Barlow`, `Host Grotesk`, `DM Sans` | Member is hitting a stale personal-preference override. Ask them to type *"forget the older Deccan design-system defaults and the IBM Plex / Aptos type stacks"* in the same chat, then re-run the prompt. |

### Check 2 — Single Deccan Blue accent

Search the CSS for `#164999`. Must appear at least once as the primary accent.

| Result | Meaning |
|---|---|
| **Pass** | `#164999` is used for headings on the cover, callout left-rule, link colour, table-header underline. No second accent hue. | Tokens are correct. |
| **Fail** | A second accent colour appears as a UI element (button background, banner band, decorative bar). Or `#71BF4D` (Deccan Green) appears outside the logo or sustainability content. | Skill is active but member has invented a second accent or misplaced the reserved green. Re-paste the prompt verbatim, or hand it to a different teammate. |

### Check 3 — Cover composition

Open the HTML in a browser. The first viewport (or page 1 of print preview) must show, top to bottom:

1. The Deccan Fine Chemicals wordmark (rule + name).
2. An eyebrow chip with the document type ("STATUS MEMO" or similar).
3. The title `Python 3.13 pilot rollout` in Deccan Blue.
4. A one-line subtitle in stone-700.
5. A five-column metadata strip — Document type · Prepared by · Date · Version · Classification.

The cover must carry **no footer and no page number**. Verify by switching to Print Preview (Ctrl+P) — the page count should be ≥ 2 and the first page's footer area should be empty.

| Result | Meaning |
|---|---|
| **Pass** | Cover renders as above, no footer. | Furniture rules from `print-rules.md` are applied. |
| **Fail** | Cover bleeds across two pages, missing elements, footer on cover. | The bundled slot template was not used. Member has overridden it or Claude generated bespoke HTML. Add to the prompt: *"Fill the bundled template at skill/assets/templates/document.html, do not write a custom one"*. |

### Check 4 — Tone

Read the body content. None of the following may appear:

- "Let me walk you through…", "I want to show you…" (first-person narrator)
- "Here's the thing:", "It's worth noting that…" (filler openings)
- "TL;DR", "deep dive", "let's dive in", "rabbit hole"
- "That said,", "Now, let's…" (casual transitions)
- Conversational subtitles in headings (`: in plain English`, `: the EOL clock is the deciding factor`)
- Decorative emoji (✅ ❌ ⚡ 💡 🔧)
- Exclamation marks
- "Imagine if…", "Think of X as Y" (mental-exercise framings)

| Result | Meaning |
|---|---|
| **Pass** | None of the patterns present. | Tone module from `tone-and-voice.md` is active. |
| **Fail** | One or more patterns present. | Skill is partially loaded — `tone-and-voice.md` likely not in the bundle, or the model is overriding it. Re-upload the skill bundle (workspace admin); confirm `references/tone-and-voice.md` is inside the zip. |

### Check 5 — Attribution

Must be run by a **non-admin member who is not the design-system maintainer**, in a fresh chat, with **no author mentioned** in the prompt.

Open the generated HTML and read the cover's "Prepared by" value.

| Result | Meaning |
|---|---|
| **Pass** | The tester's own name (derived from their account), or — only when no author could resolve — Claude **asks** who the document should be attributed to before (or while) delivering it. | Attribution policy (SKILL.md → Attribution) is active. |
| **Fail** | The design-system maintainer's personal name (any variant), the repository owner's slug, any office or executive title lifted from repository provenance, or a silently filled team/office default the tester never stated. | The session is resolving authorship from repository provenance, a maintainer persona, or a stale pre-2.4.0 default. Most common cause: the *personal* preferences block was pasted into **workspace** custom instructions — redo org-rollout Step 3 with `claude/workspace-instructions.md`. |

Grep guidance: search the HTML source for the repository owner's GitHub slug and surname — zero hits required in the document body or metadata.

Also verify rule 1 wins: re-run with "…prepare it under the QHSE team's name" → "Prepared by QHSE Team".

### Check 6 — Freshness

View source and read `<meta name="generator" content="deccan-design v2.0 · slot template X.Y.Z">`.

| Result | Meaning |
|---|---|
| **Pass** | `X.Y.Z` equals the latest release's template revision — even if the workspace bundle is a release behind. | The fetch rule (SKILL.md § "Fetching the template — hard rule") is working; bundle drift is harmless. |
| **Pass (declared fallback)** | The bundled revision, **and** the response says the fetch tool returned a rendering of the template (not source) so the bundled copy was filled. | The surface's fetch tool converts pages to markdown; the source-integrity rule (SKILL.md § "Fetching the template — hard rule") handled it correctly. Harmless while the bundle is current — keep the bundle on the latest release. |
| **Fail** | An older revision while a newer release exists and the session had network access. | The session used only the bundled copy, or a cache answered the fetch. Confirm the workspace bundle is the latest (release checklist issue), and that SKILL.md in the bundle contains the "Fetching the template — hard rule" section with the unique-query, source-integrity, and freshness-floor directives. |
| **Fail** | The response claims the canonical copy is "stale" or "below the bundled floor" because fetched content lacked the invariant markers. | Feature-presence currency test against a fetch rendering — the markers were stripped in transit by the fetch tool, not absent from the source. The installed bundle predates v2.4.1's source-integrity rule; re-upload the latest bundle. |

### Check 7 — Compact default (Prompt C)

Open Prompt C's HTML in a browser.

| Result | Meaning |
|---|---|
| **Pass** | No cover page, no end page, no revision-history or document-control block. Page one opens with the slim title block (wordmark rule + name, title in Deccan Blue, author · date meta line), and content follows on the same page. | The tier rule (SKILL.md § "Document tiers") is active. |
| **Fail** | A full-page cover, an end page, or a revision-history/document-control table appears. | The installed bundle or instruction layer predates v2.5.0 — re-upload the skill bundle and re-paste both instruction blocks. |
| **Fail** | The slim title block is missing entirely (bare `<h1>` with no wordmark or author line). | The compact template was not fetched or filled — same diagnosis path as Check 6's fetch failures. |

## Per-surface matrix

Run **Prompt B + Checks 1, 5, and 7** on each surface; Check 6 wherever network fetch is available.

| Surface | Setup | Expected |
|---|---|---|
| claude.ai web | Workspace member, fresh chat | All checks pass |
| Claude Desktop | Same account signed in | Same as web (inherits workspace skill + instructions) |
| iOS or Android app | Same account | Same as web; also confirm the document previews light-on-white in the in-app viewer |
| Claude Code | Plugin installed (`claude plugin install deccan-design@deccan`); `git config user.name` set to the tester | All checks pass; Check 5 shows the git identity |

## Interpreting the results

| Checks passing | Action |
|---|---|
| 6 of 6 | Deployment is correct. Tell the team to start using it. |
| Check 5 alone failing | Attribution leak — see Check 5's fail row; almost always the workspace-instructions paste. |
| Prompt A passes, Prompt B fails | Default-application gap — workspace custom instructions missing or stale (Step 3). |
| 2 of 6 or fewer | Likely the skill or the custom instructions are not actually applied. Re-do `org-rollout.md` Steps 2 and 3 from a clean admin session; confirm the bundle was uploaded under Workspace scope, not Personal. |
| 0 of 6 | Probable cause: the teammate is not in the workspace, or workspace skills are not yet rolled out to your tenant. Verify membership and feature availability. |

## Automated verification (Windows)

For deployments through the MSI on a Windows endpoint, the `tools/Render-DeccanDocumentPdf.ps1` helper can render any HTML deliverable to PDF and verify the page structure programmatically:

```powershell
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\response.html -Verify
```

The helper exits non-zero on failure. Useful for periodic spot-checks of generated documents or as a CI guard if Claude-produced HTML enters a downstream pipeline.

## Failure escalation

If checks fail after re-doing the rollout steps:

1. Confirm the bundle zip on the GitHub release is intact (13 files; SHA-256 visible on the release page and in SHA256SUMS.txt).
2. Confirm the workspace's custom instructions field contains the full `claude/workspace-instructions.md` block (not the personal block, not a truncated paste).
3. Open a fresh chat and prompt Claude directly: *"List the skills available in this workspace and which ones are auto-activated."* The response should include `deccan-design`.
4. Escalate to Tier 3 (design system owner — Deccan IT and Digital Transformation Team) per `admin-guide.html` §12.
