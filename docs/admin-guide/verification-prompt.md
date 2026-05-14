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

## The four binary checks

Open the HTML response in **View source** or save and open in a browser, then check each item.

### Check 1 — Sans face

Search the inline CSS for `font-family`. The first family on the sans chain must be `'Segoe UI Variable Display'`.

| Result | Meaning |
|---|---|
| **Pass** | `'Segoe UI Variable Display', 'Segoe UI Variable Text', 'Segoe UI Variable', 'Segoe UI', system-ui, …` | The skill is active. |
| **Fail** | `IBM Plex Sans`, `Hanken Grotesk`, `Aptos`, `Inter`, `Barlow`, `Host Grotesk`, `DM Sans` | Member is hitting a stale personal-preference override. Ask them to type *"forget the swiss_design_at_deccan default and the IBM Plex / Aptos type stacks"* in the same chat, then re-run the prompt. |

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

## Interpreting the results

| Checks passing | Action |
|---|---|
| 4 of 4 | Deployment is correct. Tell the team to start using it. |
| 3 of 4 | Investigate the failing check with the table guidance above. Re-test on the same teammate. |
| 2 of 4 or fewer | Likely the skill or the custom instructions are not actually applied. Re-do `org-rollout.md` Steps 2 and 3 from a clean admin session; confirm the bundle was uploaded under Workspace scope, not Personal. |
| 0 of 4 | Probable cause: the teammate is not in the workspace, or workspace skills are not yet rolled out to your tenant. Verify membership and feature availability. |

## Automated verification (Windows)

For deployments through the MSI on a Windows endpoint, the `tools/Render-DeccanDocumentPdf.ps1` helper can render any HTML deliverable to PDF and verify the page structure programmatically:

```powershell
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\response.html -Verify
```

The helper exits non-zero on failure. Useful for periodic spot-checks of generated documents or as a CI guard if Claude-produced HTML enters a downstream pipeline.

## Failure escalation

If checks fail after re-doing the rollout steps:

1. Confirm the bundle zip on the GitHub release is intact (size 47 KB, 13 files; SHA-256 visible on the release page).
2. Confirm the workspace's custom instructions field contains the full preferences block, not a truncated paste.
3. Open a fresh chat and prompt Claude directly: *"List the skills available in this workspace and which ones are auto-activated."* The response should include `deccan-design`.
4. Escalate to Tier 3 (design system owner — Office of the SVP, IT & Digital Transformation) per `admin-guide.html` §12.
