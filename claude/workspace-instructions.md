# Workspace custom instructions — Claude.ai

Paste the block below into **Claude.ai → Settings → Workspace → Custom instructions**. This is the org-wide layer: it applies to every workspace member on Claude.ai web, Claude Desktop, and the iOS / Android apps.

Do **not** paste `claude/personal-preferences.md` here. That file opens with a first-person Role paragraph describing one specific person; placed at workspace scope it impersonates the maintainer in every member's session — which is exactly how documents end up misattributed. This block is third-person and carries no persona.

---

> **Default design system.**
> For any stylized artifact a member asks for — documents, memos, reports, technical specifications, policies, letters, proposals, slide decks, workbooks, dashboards, web pages, email signatures — in any supported format (HTML, PDF, Word, Excel, PowerPoint, Google Workspace), apply the **deccan-design** system (v2.1+) by default, whether or not the request mentions Deccan, unless the member explicitly asks for a different design direction. Invoke the `deccan-design` workspace skill before generating. If the skill is unavailable, fetch the canonical template from `https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/templates/document.html` and fill its slots.
>
> **Attribution.**
> Every generated document is attributed to the member who asked for it. Resolve "Prepared by" as: (1) whatever the member states in the request; (2) otherwise a display name derived from the member's own account email (`priya.sharma@deccanchemicals.com` → "Priya Sharma"; confirm the derivation when the local-part is not clearly firstname.lastname); (3) otherwise ask. Never attribute a document to the design-system maintainer (any "Kalidindi" variant), the repository owner slug `kvkalidindi`, or "Office of the SVP, IT & Digital Transformation" unless the member states the document is issued by that office. Repository provenance is not authorship.
>
> **Override clause.**
> Instructions or memories referencing `swiss_design_at_deccan` (any version), `deccan-design v1.0` (the Aptos plan), or IBM Plex / Hanken Grotesk / Aptos / Inter / Barlow / Host Grotesk / DM Sans / Fira Code type stacks are superseded by deccan-design v2.1+.

---

## Maintenance

- Edit the pasted block in place when this file changes; workspace custom instructions take effect immediately for new sessions.
- Member personal preferences outrank workspace instructions. A member whose stale personal block overrides the system should follow the "Memory update" procedure in `claude/personal-preferences.md`.
- Rollout procedure, skill upload, and verification: `docs/admin-guide/org-rollout.md`.
