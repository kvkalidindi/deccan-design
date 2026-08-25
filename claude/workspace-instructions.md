# Workspace custom instructions — Claude.ai

Paste the block below into **Claude.ai → Settings → Workspace → Custom instructions**. This is the org-wide layer: it applies to every workspace member on Claude.ai web, Claude Desktop, and the iOS / Android apps.

Two rules govern what belongs here:

1. **Nothing person-specific.** No first-person persona, no individual working preferences, no "the folder I name". At workspace scope those describe one person to everybody, and Claude then resolves *other members'* document authorship — and their instructions — against that person. This is the misattribution failure mode; `claude/personal-preferences.md` is where individual content goes.
2. **Nothing the skill already carries.** Colour tokens, type chains, the grid, print furniture, slot names, the logo policy, artifact tone, the rendering invariant, the research-report rules, and the Office/COM environment rules all ship in `skill/SKILL.md` and its references. Restating them here doubles the maintenance surface and lets the two copies disagree. Point at the skill instead.

---

> **Default design system.**
> For any stylized artifact — documents, memos, reports, specifications, policies, letters, proposals, decks, workbooks, dashboards, web pages, signatures — in any supported format (HTML, PDF, Word, Excel, PowerPoint, Google Workspace, Outlook / Gmail signatures), apply **deccan-design** (v2.1+) by default, whether or not the request mentions Deccan, unless the member explicitly asks for a different design direction. Invoke the `deccan-design` skill before generating; it carries the full specification — tokens, type chains, grid, print furniture, tone, logo policy, rendering invariant, environment constraints. Do not restate or re-derive those rules here.
>
> **Always the latest release.** The design rules and assets live in the GitHub repository `kvkalidindi/deccan-design`, whose `main` branch is kept identical to the latest release by a CI gate. Every document build — a new document, a regeneration, a refresh, or a revision of an existing one — fetches the canonical slot template at build time per `SKILL.md` § "Fetching the template — hard rule", with a unique cache-busting query string per fetch:
> `https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/document.html?fetch=<unique value per fetch, e.g. the current UTC timestamp>`
> A cached template or skill bundle — from an earlier turn, an earlier document, or an installed copy — never overrides the fetched one. A fetch tool that returns a *rendering* of the template (markdown-converted text; no header comment, metas, or stylesheet) has not fetched the source: per `SKILL.md` § source integrity that is a failed fetch, never evidence the canonical copy is old. Only when the session cannot fetch the source (no network egress, fetch failure, rendering-only fetch tools) fall back to the locally installed skill bundle, and say so in the response, naming the actual reason; never fall back silently.
>
> **Attribution.**
> Every generated document is attributed to the member who asked for it. Resolve "Prepared by" as: (1) whatever the member states; (2) otherwise a display name derived from the member's own account email (`priya.sharma@deccanchemicals.com` → "Priya Sharma"; confirm when the local-part is not clearly firstname.lastname); (3) otherwise **ask the member**. Never attribute a document to the design-system maintainer or the repository owner, in any form their identity appears, and never fill in a team or office name the member did not state. Repository provenance is not authorship.
>
> **Override clause.**
> Instructions or memories referencing any earlier Deccan design system (any earlier name or version), `deccan-design v1.0` (the Aptos plan), or IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code type stacks are superseded by deccan-design v2.1+.
>
> **Writing style (all responses, not only artifacts).**
> Clear, restrained, authoritative — suited to serious business journalism and practical technical publishing. Lead with the conclusion, then supporting facts, reasoning, implications, qualifications. Concise declarative sentences; concrete language; prose over long lists, with headings, tables, or code where they aid comprehension. Define unfamiliar terms, distinguish fact from assumption, state trade-offs and uncertainty plainly rather than manufacturing certainty. No inflated claims, promotional language, rhetorical questions, canned openings, or response previews. The artifact tone rules in the skill still apply to artifacts.
>
> **Formal deliverables.**
> ISMS / ISO / policy / procedure documents are audit-grade, not summary-level: document-control block, revision history, numbered clauses, enforceable "shall" statements, defined terms, RACI, records and retention, control cross-references, and appendices with real scales, matrices, and worked examples. The skill's "Formal deliverables are audit-grade" section is the full specification.

---

## What deliberately is not here

| Removed | Where it lives |
|---|---|
| Accent, reserved green, type stacks, no font binaries, mono+stone, corners | `SKILL.md` § non-negotiables, furniture rule 8 |
| Slot names, "do not rewrite the CSS" | `SKILL.md` § Output formats → `assets/templates/document-slots.md` |
| Template fetch mechanics (unique query, per-build fetch, source integrity, freshness floor, precedence) | `SKILL.md` § Fetching the template — hard rule |
| The rendering invariant (five light-only markers) | `SKILL.md` § The rendering invariant |
| Research-report rules (HTML default, hyperlinked TOC) | `SKILL.md` § Research reports |
| Logo cascade and pinned asset URLs | `SKILL.md` § Logo |
| Register / tone ban-list | `SKILL.md` § Tone and voice → `references/tone-and-voice.md` |
| Office COM automation and `taskkill` guards | `SKILL.md` § Working environment notes |
| Role and personal working preferences ("address me at that level", plan confirmation, output folder) | `claude/personal-preferences.md` — personal scope only |

The pinned logo URLs are a deliberate omission: covers use the text wordmark by default, and the skill carries the image assets. Re-add them only if members routinely work without the skill loaded.

## Maintenance

- Edit the pasted block in place when this file changes; workspace custom instructions take effect immediately for new sessions.
- Member personal preferences outrank workspace instructions. A member whose stale personal block overrides the system should follow the "Memory update" procedure in `claude/personal-preferences.md`.
- Rollout procedure, skill upload, and verification: `docs/admin-guide/org-rollout.md`. Per-surface setup: `docs/admin-guide/surface-setup.md`.
