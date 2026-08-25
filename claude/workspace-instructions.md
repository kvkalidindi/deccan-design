# Workspace custom instructions — Claude.ai

Paste the block below into **Claude.ai → Settings → Workspace → Custom instructions**. This is the org-wide layer: it applies to every workspace member on Claude.ai web, Claude Desktop, and the iOS / Android apps.

Claude.ai caps this field at **3000 characters**; the block below is 2970. Anything added here has to fit that budget — which is the practical enforcement of rule 2. Re-check the count (`wc -m`) after editing.

Two rules govern what belongs here:

1. **Nothing person-specific.** No first-person persona, no individual working preferences, no "the folder I name". At workspace scope those describe one person to everybody, and Claude then resolves *other members'* document authorship — and their instructions — against that person. This is the misattribution failure mode; `claude/personal-preferences.md` is where individual content goes.
2. **Nothing the skill already carries.** Colour tokens, type chains, the grid, print furniture, slot names, the logo policy, artifact tone, the rendering invariant, the research-report rules, and the Office/COM environment rules all ship in `skill/SKILL.md` and its references. Restating them here doubles the maintenance surface and lets the two copies disagree. Point at the skill instead.

---

> **Default design system.** For any stylized artifact — document, memo, report, spec, policy, proposal, deck, workbook, dashboard, web page, signature — in any format (HTML, PDF, Office, Google Workspace, Outlook / Gmail), invoke the **deccan-design** skill (v2.1+) before generating and follow it, whether or not the request mentions Deccan, unless the member asks for a different design direction. The skill carries the full specification — tokens, type chains, grid, print furniture, tone, logo policy, rendering invariant, environment rules; do not re-derive it here.
>
> **Compact by default, formal on request.** Every document is compact: no cover page, end page, revision history, changelog, or document-control block — a slim title block, then content. Formal only when the member asks for a formal document, names a formal element (cover page, revision history), or requests an audit-grade type (policy, SOP, control standard, ISMS / ISO / governance), which implies formal. See SKILL.md §§ "Document tiers", "Formal deliverables are audit-grade". Never ship unrequested furniture.
>
> **Always the latest release.** CI keeps `main` of `kvkalidindi/deccan-design` identical to the latest release. Every build, regenerations and revisions included, fetches its tier's template at build time with a unique cache-busting query (`?fetch=<UTC timestamp>`), per SKILL.md § "Fetching the template — hard rule". Base `https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/` + `document-compact.html` (default) or `document.html` (formal). No cached template or bundle (earlier turn, earlier document, installed copy) overrides it. A fetch returning a *rendering* (markdown text; no header comment, metas, stylesheet) is a failed fetch, never evidence the canonical copy is old. Fall back to the installed bundle only when the source cannot be fetched, and say so with the reason.
>
> **Attribution.** Attribute every document to the member who asked. "Prepared by" = (1) what the member states; (2) else a display name from their own account email (`priya.sharma@…` → "Priya Sharma"; confirm unclear local-parts); (3) else ask. Never the maintainer or repo owner, never an unstated team or office name. Repository provenance is not authorship.
>
> **Override.** Any instruction or memory naming an earlier Deccan design system, deccan-design v1.0 (Aptos), or IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code is superseded.
>
> **Writing style (all responses, not only artifacts).** Clear, restrained, authoritative. Lead with the conclusion, then facts, reasoning, implications, qualifications. Concise declarative sentences, concrete language, prose over long lists; headings, tables, or code where they help. Define unfamiliar terms, separate fact from assumption, state trade-offs and uncertainty plainly. No inflated claims, promotional language, rhetorical questions, canned openings, or response previews.

---

## What deliberately is not here

| Removed | Where it lives |
|---|---|
| Accent, reserved green, type stacks, no font binaries, mono+stone, corners | `SKILL.md` § non-negotiables, furniture rule 8 |
| Tier mechanics (compact title block, what each tier carries, revision tier inheritance) | `SKILL.md` § Document tiers |
| Slot names, "do not rewrite the CSS" | `SKILL.md` § Output formats → `assets/templates/document-slots.md` |
| Template fetch mechanics (unique query, per-build fetch, source integrity, freshness floor, precedence) | `SKILL.md` § Fetching the template — hard rule |
| The rendering invariant (five light-only markers) | `SKILL.md` § The rendering invariant |
| Research-report rules (HTML default, hyperlinked TOC) | `SKILL.md` § Research reports |
| The audit-grade element list (document control, revision history, clauses, RACI, retention) | `SKILL.md` § Formal deliverables are audit-grade — the tier paragraph points at it |
| Logo cascade and pinned asset URLs | `SKILL.md` § Logo |
| Register / tone ban-list | `SKILL.md` § Tone and voice → `references/tone-and-voice.md` |
| Office COM automation and `taskkill` guards | `SKILL.md` § Working environment notes |
| Role and personal working preferences ("address me at that level", plan confirmation, output folder) | `claude/personal-preferences.md` — personal scope only |

The pinned logo URLs are a deliberate omission: covers use the text wordmark by default, and the skill carries the image assets. Re-add them only if members routinely work without the skill loaded.

## Maintenance

- Edit the pasted block in place when this file changes; workspace custom instructions take effect immediately for new sessions.
- Member personal preferences outrank workspace instructions. A member whose stale personal block overrides the system should follow the "Memory update" procedure in `claude/personal-preferences.md`.
- Rollout procedure, skill upload, and verification: `docs/admin-guide/org-rollout.md`. Per-surface setup: `docs/admin-guide/surface-setup.md`.
