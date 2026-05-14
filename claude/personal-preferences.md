# Personal preferences — Claude.ai

Paste the text below into **Claude.ai → Settings → Profile → Preferences**. This is a one-time configuration per Claude.ai account.

The block is also the canonical reference used by the `deccan-design` skill (Claude Code, Claude Desktop, Cowork). Updating it here keeps every Claude surface aligned.

---

> ## Default design system
>
> Default design system for all generated documents, slide decks, web pages, UI mockups, reports, diagrams, brand artifacts, and any styled output: **`deccan-design`** (v2.0+). Apply the system unless I explicitly request a different style by name.
>
> **Override clause.** Older instructions referencing `swiss_design_at_deccan` (any version), `deccan-design v1.0` (the Aptos plan), or IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code type stacks are superseded. Apply `deccan-design v2.0+` only, with the Segoe UI Variable / Cascadia Mono OS-native stack and the colour tokens documented at `https://github.com/kvkalidindi/deccan-design/blob/main/skill/references/tokens.md`.
>
> ### Type stack (OS-native, no font binaries)
>
> - **Sans:** `'Segoe UI Variable Display', 'Segoe UI Variable Text', 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif`
> - **Mono:** `'Cascadia Mono', 'Cascadia Code', Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', ui-monospace, monospace`
>
> ### Colour tokens
>
> - **Primary accent:** `--deccan-blue: #164999`. Single accent; hierarchy via opacity stops (90 / 60 / 30 / 15).
> - **Reserved colour:** `--deccan-green: #71BF4D` — logo and sustainability content only. Never a UI accent.
> - **Neutral:** `--stone-50` `#FAFAF9` through `--stone-900` `#1C1917`.
> - **Paper:** `#FFFFFF`.
>
> ### Document furniture (eight rules)
>
> Self-contained cover with logo + title + subtitle + author + version + date + classification. No header / footer / page number on cover or end page. Every H1 starts on a new page. Body fills the live content area. Bare-integer page numbers, right-aligned. Pure white print background; stone tints only in callouts, code blocks, banded table rows, and chips. Mono and stone always travel together.
>
> ### Tone and voice
>
> Direct, declarative, third-person. Plain noun-phrase headings — never conversational subtitles. No first-person narrator asides ("Let me walk you through…"), filler openings ("Here's the thing:"), casual transitions ("That said,"), "deep dive" / "TL;DR" / "rabbit hole", decorative emoji, or exclamation marks in body prose. The full ban-list is in `skill/references/tone-and-voice.md` of the repository.
>
> ### Working-environment rules (Windows 11 corporate machine)
>
> - **Don't use Office COM automation** (Word.Application, Excel.Application, PowerPoint.Application). The corporate install hangs silently on Trust Center / license dialogs. To verify a document, ask me to export from the Office UI, or use LibreOffice headless if available. Don't `taskkill` the Office processes.
> - **Project layout:** put output directly in the user-designated folder. No nested project-named subfolders.
> - **No font binaries** in generated artifacts. The OS-native chain is the policy.
> - **PDF generation is on-demand by the user**: File → Export → Create PDF/XPS from Office, or `wkhtmltopdf` against HTML. Don't render PDFs in a sandbox where fonts will substitute.
>
> ### Skill reference
>
> The authoritative skill is at `https://github.com/kvkalidindi/deccan-design`. The Anthropic skill module is in `skill/SKILL.md`; the slot-fill HTML template is at `skill/assets/templates/document.html`. The deployment package (Office templates, Outlook signature, Claude skill, documentation) ships via the v2.0.0 GitHub release as an unsigned MSI (Windows) and PKG (macOS).

---

## Memory update (for the Claude memory subsystem)

Update persistent memory:

- **Remove** any line referencing `swiss_design_at_deccan` as the default design system.
- **Remove** any line referencing IBM Plex, Hanken Grotesk, Barlow, Host Grotesk, DM Sans, or Fira Code as a default or fallback.
- **Remove** any line referencing the Aptos plan or `deccan-design v1.0`.
- **Add** an entry: "Default design system is `deccan-design` v2.0+. Type stack is OS-native: Segoe UI Variable on Windows 11, Segoe UI on Windows 10, San Francisco via `system-ui` on macOS. Mono stack is Cascadia Mono / Consolas. Skill repository at `https://github.com/kvkalidindi/deccan-design`."

The memory update is performed by Claude.ai automatically when the preferences block above is saved. If a stale memory persists after the preferences update, ask Claude to "forget the `swiss_design_at_deccan` default" or "forget the IBM Plex chain" directly.

## Verification

After saving the preferences, verify with this prompt in any Claude surface:

> "Generate a one-page status memo for Deccan Fine Chemicals on the Python 3.13 pilot."

A correct response uses the deccan-design v2.0 stack: Segoe UI Variable in the document body, Cascadia Mono for any code, Deccan Blue (`#164999`) as the only accent, no banned tone-and-voice patterns. The skill `deccan-design` is invoked automatically and the document conforms to the eight document-furniture rules.

If the response uses IBM Plex Sans, Aptos, Inter, or any banned face — the preferences did not save, or a memory override is still in effect. Re-paste the preferences block and prompt Claude to forget the older defaults.
