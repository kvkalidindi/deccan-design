# Organization rollout — Claude.ai workspace deployment

Procedure for deploying the `deccan-design` system to a Claude.ai workspace so it applies to every member without per-user configuration.

This document covers Claude.ai only. The Windows MSI (Office templates, Outlook signature, Claude Code / Claude Desktop skill, offline reference docs) is documented in `admin-guide.html` §03–§05.

## Prerequisites

| Item | Requirement |
|---|---|
| Plan | Claude **Team** or **Enterprise**. Org-level Skills upload requires Enterprise; some Team plans see it in private preview. Org-level Custom instructions are available on both. |
| Role | Workspace admin (formerly "Owner") for the Deccan Fine Chemicals workspace. |
| Bundle | `deccan-design-skill-bundle.zip` from the **latest** `v*` GitHub release (<https://github.com/kvkalidindi/deccan-design/releases/latest>). 13 files, single top-level folder `deccan-design/`. Built from the tagged tree by the `release-design-system` workflow. |
| Workspace instructions | `claude/workspace-instructions.md` in the repo — the org-wide block. (`claude/personal-preferences.md` is the *personal* block; it must never be pasted at workspace scope — see Step 3.) |

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
   - Parses the frontmatter — expects `name`, `description`, `version`. The skill ships with `name: deccan-design` and the `version` of the release you downloaded — that value is what the workspace skill list shows, so it is how you confirm which bundle is live.
   - Refuses bundles that contain executable code, oversized assets, or invalid frontmatter. The deccan-design bundle is markdown + HTML + image / vector assets only and passes cleanly.
5. **Distribution scope.** Select **All workspace members**. (If the workspace uses SCIM-synced groups, scoping by group is supported; for the design system, all-members is correct.)
6. **Activation behaviour.** Select **Auto-activate** so the skill loads in every member's session by default. The alternative — *Discoverable* — requires each user to enable it manually and slows adoption to a crawl.
7. Click **Publish**. The skill becomes available to every targeted member within a few minutes. Claude.ai caches the workspace skill manifest at session start, so existing sessions may need a refresh to pick up the new skill.

## Step 3 — Set workspace custom instructions

This is the policy layer: it makes deccan-design the default for **any** stylized document (not only Deccan-named requests) and sets the attribution rule for every member.

1. **Settings → Workspace → Custom instructions** (sometimes labelled **Default preferences** or **System prompt**).
2. Open `claude/workspace-instructions.md` from the repository.
3. Copy the block (everything inside the `>` blockquote).
4. Paste into the workspace custom-instructions field.
5. Save.

**Use `workspace-instructions.md`, never `personal-preferences.md`.** The personal file opens with a first-person Role paragraph describing one individual; pasted at workspace scope it impersonates that person in every member's session, and Claude then attributes members' documents to the design-system maintainer. If a previous rollout pasted the personal block here, replacing it with the workspace block is the fix.

The block establishes `deccan-design` v2.1+ as the default for any stylized artifact, carries the attribution rule ("Prepared by" = the requesting member, never the maintainer), and retires `swiss_design_at_deccan`, IBM Plex, Hanken Grotesk, Aptos, Inter, Barlow, Host Grotesk, DM Sans, and Fira Code references. Claude composes preferences in priority order (User > Workspace > Default); the workspace block becomes the floor.

## Step 3b — Claude Code (plugin marketplace)

Claude Code takes the skill from this repository's plugin marketplace — the only channel that updates itself when the repo changes.

**Self-serve (any developer, one time):**

```
claude plugin marketplace add kvkalidindi/deccan-design
claude plugin install deccan-design@deccan
```

Updates then arrive automatically from `main`; no re-install per release.

**Org-enforced (managed fleet):** push managed settings via Intune / Jamf to
`C:\ProgramData\ClaudeCode\managed-settings.json` (Windows) or
`/Library/Application Support/ClaudeCode/managed-settings.json` (macOS):

```json
{
  "extraKnownMarketplaces": {
    "deccan": { "source": { "source": "github", "repo": "kvkalidindi/deccan-design" } }
  },
  "enabledPlugins": { "deccan-design@deccan": true }
}
```

Optionally deploy a managed `CLAUDE.md` beside it carrying the same default-design and attribution directive as the workspace block. Managed settings refresh on startup and hourly, so the fleet follows the repo without further pushes.

The MSI's `%APPDATA%\Anthropic\Claude\skills\deccan-design\` copy is **legacy**: superseded by the plugin for Claude Code, and by the workspace skill for Claude Desktop. It may be removed from a future installer build; until then it is harmless but perpetually stale.

## Step 4 — Notify the team

Send a short comms email. Suggested copy:

```
Subject: Claude.ai — deccan-design is now the default

Hi team,

We have set deccan-design as the workspace-level default design system
in Claude.ai. From your next new chat:

- Any document / memo / brief / deck / spreadsheet request — whether
  or not it mentions Deccan — will produce a compliant artifact
  automatically, attributed to you (not to the design-system owner).
- No personal-preferences paste required from your side, but if you
  had IBM Plex / Aptos / swiss_design_at_deccan defaults set
  previously, ask Claude to "forget those defaults" in any chat to
  evict them from your memory.
- Claude Code users: run
  `claude plugin marketplace add kvkalidindi/deccan-design` and
  `claude plugin install deccan-design@deccan` once — updates are
  automatic afterwards.
- The MSI installer on the releases page still brings the Word /
  Excel / PowerPoint templates and the Outlook signature to your
  laptop.

Questions: <your IT contact>.
```

## Step 5 — Verify activation

Use the procedure in `verification-prompt.md` (next to this file). Hand Prompt B to any non-admin teammate — it deliberately omits the word "Deccan" — run through the six binary checks (including attribution and freshness), and report back. The per-surface matrix at the end of that file covers web, Desktop, mobile, and Claude Code.

## Maintenance

- **Skill updates.** When a new version of `deccan-design` ships, push the `v*` tag: the `release-design-system` workflow builds `deccan-design-skill-bundle.zip` from the tagged tree, attaches it to the release, and **opens a checklist issue assigned to the workspace admin** with the re-upload steps — the manual step cannot be silently forgotten. Re-upload via **Settings → Workspace → Skills → deccan-design → Replace bundle**; members pick up the new version on next session, and the frontmatter `version` in the skill list confirms which bundle is live. Additionally set **Watch → Custom → Releases** on the repository.

  Drift is bounded either way: the skill's "Staying current" rule has sessions fetch the canonical slot template from the repository at generation time when the network allows, so even a lagging workspace bundle produces current documents.

  Claude Code needs nothing per release — the plugin channel follows `main` automatically. The MSI / PKG skill copy is legacy (see Step 3b) and no longer part of the release loop.
- **Preferences updates.** Edit the workspace custom instructions in place. Changes take effect immediately for new sessions.
- **Deprecation.** To retire `deccan-design`, remove the skill via **Settings → Workspace → Skills → deccan-design → Remove** and clear the workspace custom instructions. Members fall back to per-user preferences. No data is destroyed.

## Caveats

- Claude.ai's admin UI evolves. The menu paths above are accurate as of May 2026 — if labels differ in your tenant, search for the nearest match. The semantics do not change.
- Workspace skills do not propagate to **Cowork** or to standalone API access — those surfaces are skill-aware via different mechanisms (API uses an explicit `skills` parameter; Cowork inherits from the user's Claude.ai workspace).
- The MSI's `%APPDATA%\Anthropic\Claude\skills\deccan-design\` install (for Claude Code and Claude Desktop) is independent of the workspace skill. Both must be deployed for full coverage. The MSI ships unsigned by design (PRD §1.4 Decision 5); see `admin-guide.html` §06 for the SmartScreen runbook.
