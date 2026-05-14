# Organization rollout — Claude.ai workspace deployment

Procedure for deploying the `deccan-design` system to a Claude.ai workspace so it applies to every member without per-user configuration.

This document covers Claude.ai only. The Windows MSI (Office templates, Outlook signature, Claude Code / Claude Desktop skill, offline reference docs) is documented in `admin-guide.html` §03–§05.

## Prerequisites

| Item | Requirement |
|---|---|
| Plan | Claude **Team** or **Enterprise**. Org-level Skills upload requires Enterprise; some Team plans see it in private preview. Org-level Custom instructions are available on both. |
| Role | Workspace admin (formerly "Owner") for the Deccan Fine Chemicals workspace. |
| Bundle | `deccan-design-skill-bundle.zip` from the v2.0.1 GitHub release: <https://github.com/kvkalidindi/deccan-design/releases/download/v2.0.1/deccan-design-skill-bundle.zip>. 47 KB, 13 files, single top-level folder `deccan-design/`. |
| Preferences text | `claude/personal-preferences.md` in the repo, also bundled in the MSI at `%APPDATA%\deccan-design\docs\personal-preferences.md`. |

## Step 1 — Verify availability

1. Sign in to <https://claude.ai> as a workspace admin.
2. Click your name in the bottom-left → **Settings**.
3. Switch to **Workspace** scope (toggle at the top of Settings between *Personal* and *Workspace*).
4. Look in the left-side admin nav for **Skills**. The label may also appear as **Capabilities** or **Tools** in some rollout cohorts.
5. If **Skills** is not present, your workspace does not yet have the feature. Skip to Step 3 (preferences) and revisit Step 2 (skill upload) when the feature ships.

## Step 2 — Upload the skill bundle

1. Download `deccan-design-skill-bundle.zip` from the release URL above. Do not unzip it; Claude.ai accepts the zip directly.
2. In **Settings → Workspace → Skills**, click **Add skill** (or **Upload skill** / **+ Skill** depending on label).
3. Drop the zip into the upload area, or browse to it.
4. Claude.ai validates the bundle:
   - Checks `SKILL.md` is present at the root of `deccan-design/` inside the zip.
   - Parses the frontmatter — expects `name`, `description`, `version`. The skill ships with `name: deccan-design`, `version: 2.0.0`.
   - Refuses bundles that contain executable code, oversized assets, or invalid frontmatter. The deccan-design bundle is markdown + HTML + image / vector assets only and passes cleanly.
5. **Distribution scope.** Select **All workspace members**. (If the workspace uses SCIM-synced groups, scoping by group is supported; for the design system, all-members is correct.)
6. **Activation behaviour.** Select **Auto-activate** so the skill loads in every member's session by default. The alternative — *Discoverable* — requires each user to enable it manually and slows adoption to a crawl.
7. Click **Publish**. The skill becomes available to every targeted member within a few minutes. Claude.ai caches the workspace skill manifest at session start, so existing sessions may need a refresh to pick up the new skill.

## Step 3 — Set workspace custom instructions

This is the policy layer. Without it, members with stale personal preferences referencing `swiss_design_at_deccan` or IBM Plex can override the org skill.

1. **Settings → Workspace → Custom instructions** (sometimes labelled **Default preferences** or **System prompt**).
2. Open `claude/personal-preferences.md` from the repository or from the local MSI install at `%APPDATA%\deccan-design\docs\personal-preferences.md`.
3. Copy the entire block (everything inside the `>` blockquote in that file).
4. Paste into the workspace custom-instructions field.
5. Save.

The block establishes `deccan-design` v2.0+ as the default and carries the explicit **override clause** that retires `swiss_design_at_deccan`, IBM Plex, Hanken Grotesk, Aptos, Inter, Barlow, Host Grotesk, DM Sans, and Fira Code references. Claude composes preferences in priority order (User > Workspace > Default); the workspace block becomes the floor, ensuring even users with empty personal preferences still get the deccan-design defaults.

## Step 4 — Notify the team

Send a short comms email. Suggested copy:

```
Subject: Claude.ai — deccan-design is now the default

Hi team,

We have set deccan-design as the workspace-level default design system
in Claude.ai. From your next new chat:

- Any "make a Deccan document / memo / brief / deck / spreadsheet"
  request will produce a v2.0-compliant artifact automatically.
- No personal-preferences paste required from your side, but if you
  had IBM Plex / Aptos / swiss_design_at_deccan defaults set
  previously, ask Claude to "forget those defaults" in any chat to
  evict them from your memory.
- The MSI installer at
  https://github.com/kvkalidindi/deccan-design/releases/tag/v2.0.1
  brings the same defaults to Claude Code, Claude Desktop, Word,
  Excel, PowerPoint, and Outlook on your laptop.

Questions: <your IT contact>.
```

## Step 5 — Verify activation

Use the procedure in `verification-prompt.md` (next to this file). Hand the prompt to any non-admin teammate, run through the four binary checks, and report back.

## Maintenance

- **Skill updates.** When a new version of `deccan-design` ships (e.g., v2.1), rebuild the bundle (the GitHub release for the new tag will carry it), and re-upload via **Settings → Workspace → Skills → deccan-design → Replace bundle**. Members pick up the new version on next session.
- **Preferences updates.** Edit the workspace custom instructions in place. Changes take effect immediately for new sessions.
- **Deprecation.** To retire `deccan-design`, remove the skill via **Settings → Workspace → Skills → deccan-design → Remove** and clear the workspace custom instructions. Members fall back to per-user preferences. No data is destroyed.

## Caveats

- Claude.ai's admin UI evolves. The menu paths above are accurate as of May 2026 — if labels differ in your tenant, search for the nearest match. The semantics do not change.
- Workspace skills do not propagate to **Cowork** or to standalone API access — those surfaces are skill-aware via different mechanisms (API uses an explicit `skills` parameter; Cowork inherits from the user's Claude.ai workspace).
- The MSI's `%APPDATA%\Anthropic\Claude\skills\deccan-design\` install (for Claude Code and Claude Desktop) is independent of the workspace skill. Both must be deployed for full coverage. The MSI ships unsigned by design (PRD §1.4 Decision 5); see `admin-guide.html` §06 for the SmartScreen runbook.
