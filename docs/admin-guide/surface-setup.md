# Surface setup — one behaviour on every Claude surface

Configuration per Claude surface so that deccan-design behaves identically everywhere:

1. **Default-on.** The skill is invoked for any stylized deliverable, whether or not the request mentions Deccan.
2. **Latest release, always.** Every document build fetches the canonical template from the repo's `main` branch — which a CI release gate keeps identical to the latest release — with a unique cache-busting query string per fetch.
3. **Caches never override.** A template or skill bundle held in conversation context, memory, or an installed copy never overrides the fetched one. No network egress → fall back to the installed skill bundle, and say so.
4. **Attribution.** "Prepared by" = stated author → the requesting user's identity → **ask**. Never a maintainer name, never a silent default.

The skill itself (`skill/SKILL.md`) carries all four rules; the per-surface work is making sure the skill is installed, current, and not fighting a stale instruction or memory layer.

## Claude.ai web, Claude Desktop, iOS / Android

Claude Desktop and the mobile apps inherit the Claude.ai account's workspace skills, custom instructions, personal preferences, and memory — configure Claude.ai once and all four surfaces follow.

**Org layer (workspace admin, once per release):**

1. Upload `deccan-design-skill-bundle.zip` from the [latest release](https://github.com/kvkalidindi/deccan-design/releases/latest) via **Settings → Workspace → Skills** (auto-activate, all members). Full procedure: `org-rollout.md` Step 2.
2. Paste the block from `claude/workspace-instructions.md` into **Settings → Workspace → Custom instructions**. Re-paste only when that file changes.
3. Per release: the tag automatically opens a checklist issue; follow it (re-upload bundle, confirm version, re-run verification).

**Personal layer (each member, once):**

1. Paste the block from `claude/personal-preferences.md` into **Settings → Profile → Preferences**.
2. Run the "Memory update" procedure at the end of that file to evict stale defaults.

**Network note.** Claude.ai's fetch tool can reach `raw.githubusercontent.com`; the per-build fetch works on all four surfaces. If a session reports it cannot fetch, it uses the workspace-installed bundle and must say so.

## Claude Code (CLI and desktop-app terminal)

The plugin marketplace is the channel — it follows `main` automatically, so no per-release action exists.

```
claude plugin marketplace add kvkalidindi/deccan-design
claude plugin install deccan-design@deccan
```

- Managed fleets: push `managed-settings.json` instead — see `org-rollout.md` Step 3b.
- Attribution rule 2 resolves from `git config user.name` (else the git email local-part) — ensure it is set on the machine.
- The MSI / PKG skill copy under `%APPDATA%\Anthropic\Claude\skills\` / `~/Library/Application Support/Anthropic/Claude/skills/` is legacy and perpetually stale; the plugin supersedes it. Remove it if both are present and disagreeing.

## Claude Code on the web (remote / cloud sessions)

Same plugin channel as the CLI — a repository that carries `.claude-plugin/marketplace.json` loads the skill when the session's configuration includes it, and a session working *in this repo* picks the plugin up directly.

Two web-specific checks:

- **Network policy.** The session's environment must allow egress to `raw.githubusercontent.com` (and `github.com`) for the per-build template fetch. With a restrictive policy, add those hosts to the allowlist; otherwise every build falls back to the bundled copy — permitted, but every response must say so.
- **Identity.** Attribution rule 2 uses the session's git identity; in fresh containers confirm `git config user.name` before generating documents, else the session must ask (rule 3).

## Memory hygiene (all surfaces)

Memory is the one layer that can silently reintroduce staleness on every surface at once. Two rules:

**Belongs in memory:**

- "deccan-design (repo `kvkalidindi/deccan-design`) is the default design system for every stylized artifact."
- "Always the latest release: the template is fetched at build time; currency comes from the fetch, never from memory."

**Never belongs in memory — evict on sight:**

- Any memory pinning a package version or template revision as "current", "canonical", or "confirmed" (e.g. "v2.2 template confirmed as canonical"). Versions move; the memory does not. This is the stale-cache failure mode in its most durable form.
- Cached template contents, rule bodies, colour values, or type chains "remembered" from earlier sessions. The skill and the fetched template are the source; a remembered copy is a cache and must never override them.
- Any earlier Deccan design-system name or type stack (superseded — see the override clause in both instruction blocks).

To evict: in any chat, ask Claude to forget the specific memory ("forget that v2.2 is the canonical template — currency is established per build by fetching from the repo"), then verify with the prompt in `verification-prompt.md`.

## Verification

Run `verification-prompt.md` (Prompt B + the six checks) per surface after any configuration change. The per-surface matrix at the end of that file states what each surface should show.
