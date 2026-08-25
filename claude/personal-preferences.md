# Personal preferences — Claude.ai

Paste the text below into **Claude.ai → Settings → Profile → Preferences**, replacing the current block in its entirety. One-time configuration per Claude.ai account.

> **Admins:** this is the *personal* block — the Role paragraph describes the individual account holder. Never paste it into **Workspace → Custom instructions**; at workspace scope it impersonates one person in every member's session and misattributes their documents. The workspace layer uses `claude/workspace-instructions.md` instead.

Like the workspace block, this layer carries only what the skill cannot: personal identity, personal working preferences, and the pointers that make the skill load and stay current. Everything else — tokens, type chains, print rules, mono/code styling, the tone ban-list, the rendering invariant — ships in the skill and is deliberately not restated here.

The preferences field shares the workspace field's **3000-character** limit; the block below is 2962. Re-check the count after editing — the budget is what keeps this layer from re-absorbing the skill.

**Not in the block, on purpose:** the pinned logo URLs (the block points at `SKILL.md` § Logo, which lists them) and the Claude Code registration steps, which are setup documentation rather than a preference — they live in `docs/admin-guide/surface-setup.md` and are reproduced under "Claude Code registration" below.

---

> **Role and tone.** I am a senior engineering leader at Deccan Fine Chemicals (Hyderabad, India), working on internal tooling, design systems, and AI workflows. Address me at that level. Skip preambles and recap summaries. For non-trivial tasks (3+ steps), confirm the plan once before implementing. After corrections, capture the lesson rather than apologise.
>
> **Default design system.** For any stylized artifact (documents, web pages, decks, workbooks, dashboards, signatures), whether or not the request mentions Deccan, invoke the **`deccan-design`** skill (v2.1+) and follow it. It carries the full specification; do not re-derive its rules from memory, and never let an older memorised Deccan default override it.
>
> **Compact by default, formal on request.** Every document is compact — no cover page, end page, revision history, changelog, or document-control block; a slim title block, then content — unless I ask for a formal document, name a formal element, or request an audit-grade type (policy, SOP, ISO / ISMS), which implies formal. SKILL.md § "Document tiers".
>
> **Always the latest release.** CI keeps `main` of `kvkalidindi/deccan-design` identical to the latest release. Every build, regenerations and revisions included, fetches its tier's canonical template from `main` at build time with a unique cache-busting query, per SKILL.md § "Fetching the template — hard rule". No cached template or bundle from an earlier turn overrides it. A fetch returning a *rendering* (markdown text, no stylesheet) is a failed fetch, never evidence the canonical copy is old. Fall back to my installed skill only when the source cannot be fetched, and say so with the reason.
>
> **Attribution.** Attribute documents I request to me: my explicit statement, else my account identity (display name from my email), else ask me. Never the design-system maintainer, the repo owner slug, or a team or office name I did not state.
>
> **Override.** Older instructions or memories naming any earlier Deccan design system, `deccan-design v1.0` (Aptos), or IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code are superseded; treat an earlier system name as an alias for `deccan-design`. A memory pinning a version or template revision as "current" is stale by definition — currency comes from the per-build fetch.
>
> **Logo.** Bundled skill asset first, then project `data/logo.png`, then the pinned raw GitHub URLs in SKILL.md § Logo. Never from `deccanchemicals.com` — an emitter that does is broken; rewrite it.
>
> **Working environment.** Managed corporate Windows machine with Office. Never use COM automation (`Word.Application` etc.) to render Office files to PDF — it hangs on Trust Center dialogs. Ask me to run File → Export → Create PDF/XPS, or suggest LibreOffice headless. Never propose killing Office processes.
>
> **Project layout.** Put project output directly in the folder I name. Never nest a project-named subfolder inside it.

---

## Claude Code registration (reference, not part of the pasted block)

The `deccan-design` skill reaches Claude Code through the repository's plugin marketplace — `claude plugin marketplace add kvkalidindi/deccan-design`, then `claude plugin install deccan-design@deccan`, one-time; updates arrive automatically from `main`. The MSI / PKG copy at `%APPDATA%\Anthropic\Claude\skills\deccan-design\` (Windows) or `~/Library/Application Support/Anthropic/Claude/skills/deccan-design/` (macOS) is legacy and may lag; the installers remain the channel for Office templates and the Outlook signature. Full per-surface procedure: `docs/admin-guide/surface-setup.md`.

## Verification

After saving the preferences, verify with this prompt in any Claude surface:

> "Generate a one-page Deccan status memo for the Python 3.13 pilot rollout."

A correct response invokes the `deccan-design` skill automatically, fetches the canonical **compact** template (with a cache-busting query string) for the build, and produces a **compact** document in the deccan-design v2.0 stack: slim title block (no cover page, no end page, no revision history), Segoe UI Variable in the body, Cascadia Mono for any code, Deccan Blue (`#164999`) as the only accent, attributed to you. A full cover page on this prompt means the installed bundle predates v2.5.0 — re-upload it.

If the response uses IBM Plex Sans, Aptos, Inter, or any banned face — the preferences did not save, or a memory override is still in effect. Re-paste the preferences block and prompt Claude to forget the older defaults.

## Memory update (for the Claude memory subsystem)

When the preferences block above is saved, ask Claude (in the same session) to:

- Forget any earlier Deccan default design system, under any earlier name.
- Forget the IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code type stacks.
- Forget any earlier Deccan design-system skill name as a separate skill (each is now an alias for `deccan-design`).
- Forget any memory that pins a specific deccan-design package version or template revision as "current" or "canonical" — currency is established per build by fetching from the repo, never from memory.
- Remember only this: `deccan-design` (repo `kvkalidindi/deccan-design`) is the default design system for every stylized artifact; the latest release is always used, fetched at build time.
