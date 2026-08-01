# Changelog

Package releases of the deccan-design system. The **design system itself is v2.0** — its rules (tokens, type stack, grid, the eight document-furniture rules) have not changed. Package versions carry the skill, the templates, and the tooling that delivers them.

Two release lines share this repository:

- `v*` — the design system: skill bundle and templates bundle, built by `release-design-system.yml`.
- `converter-v*` — Deccan Convert, the document converter binary, built by `release-converter.yml`.

---

## v2.1.2 — 1 August 2026

**Audit-grade rule moved into the skill.** ISMS / ISO / policy / procedure deliverables must carry a document-control block, revision history, numbered clauses, enforceable "shall" statements, defined terms, RACI, records and retention, control cross-references, and appendices with real instruments. This existed only in the Claude.ai workspace instructions, so it applied on one surface; it is now `SKILL.md` § "Formal deliverables are audit-grade" and reaches every surface, with a verification-checklist item.

**Workspace instructions trimmed** to what only the workspace layer can carry — default-application trigger, attribution, override clause, response-wide writing style. Guards, slot names, template-fetch rule, logo cascade, register, and Office/COM notes were removed as redundant with the skill; `claude/workspace-instructions.md` now documents where each removed rule lives and the two rules for what belongs at workspace scope.

## v2.1.1 — 1 August 2026

**Fixed the skill upload.** Claude.ai rejects a SKILL.md `description` over 1024 characters; v2.1.0's was 1206, so the bundle could not be uploaded. Rewritten to 1016 with no content lost. `build_bundles.py` now runs `verify_frontmatter()` on every build and check, so a bundle the uploader would refuse can no longer be published.

## v2.1.0 — 1 August 2026

Three changes to how the system reaches and behaves for the organization.

**Default application.** The skill triggered only on Deccan-named requests. Its description now covers any stylized or formatted deliverable in any supported format, whether or not Deccan is mentioned, with an explicit escape for a user-requested design direction. The same directive is expressed in the workspace instructions, the managed-settings guidance for Claude Code, and the personal preferences block.

**Attribution.** Documents were being attributed to the design-system maintainer. No hardcoded name existed anywhere in the repository — the cause was the rollout guide instructing admins to paste the *personal* preferences block, which opens with a first-person persona, into *workspace* custom instructions. `SKILL.md` § Attribution now defines the resolution order (stated author → session identity → ask) and the prohibited evidence (repo slug, maintainer name, repo documentation, the illustrative office). A new persona-free `claude/workspace-instructions.md` replaces the personal block at workspace scope.

**Distribution.** The repository became a Claude Code plugin marketplace (`.claude-plugin/marketplace.json` + `plugin/`), the only channel that follows `main` automatically; the MSI's skill copy is demoted to legacy. `SKILL.md` § "Staying current" has sessions compare the bundled and canonical template revisions at generation time, so a lagging workspace bundle still produces current documents. Every `v*` release now opens a checklist issue for the workspace admin, because no API exists to push the workspace bundle.

Enforcement: `verify_attribution()` and the plugin-mirror byte-equality check fail the build if any of this is dropped.

## v2.0.3 — 1 August 2026

**The slot template names its own revision.** The rendering fix had been live since v2.0.2, but the file gave a reader no way to tell which copy they had fetched — the only version string in it named the design system. A header comment and `<meta name="generator">` now carry the template revision, and the generator meta rides into every produced document. `build_bundles.py` refuses to build a release whose template marker disagrees with the skill version.

## v2.0.2 — 1 August 2026

**Documents no longer render dark-on-dark in in-app previews.** The template set its page background only through `body`, which a preview host's dark canvas overrides — leaving dark stone text on a dark background everywhere except blocks with their own background. The template now carries a light-only rendering contract: `color-scheme: light only`, canvas pinned above the specificity of an injected rule, opaque structural surfaces, and a `prefers-color-scheme: dark` block re-asserting light values. `@media print` restores pure white at matching specificity.

**Body gutter restored.** `main.body`'s padding shorthand outranked `.shell`, zeroing the horizontal gutter and running body copy into both screen edges on a phone.

**Release bundles automated.** `tools/release/build_bundles.py` + `release-design-system.yml` build both bundles from the tagged tree with byte-stable zips, replacing hand-zipped uploads that had drifted from the committed sources.

## v2.0.1 — 14 May 2026

Windows package refresh: the MSI now bundles the full skill tree (references, slot template, assets) that v2.0.0 omitted, plus cover and end-page print-rendering fixes.

## v2.0.0 — 14 May 2026

First release of the v2.0 system: OS-native type stack, Deccan Blue single accent, 12-column 8px grid, the eight document-furniture rules, Office / Workspace / Outlook templates, and the Claude skill.

---

# Deccan Convert

## 1.1.0 — 1 August 2026

**Self-update on launch.** The binary had no update path, so an endpoint kept whatever build it first downloaded — including the design kit frozen inside it. It now checks the pinned repository's `converter-v*` releases at most once a day, verifies the artifact against the SHA-256 in that release's own `SHA256SUMS.txt`, and swaps itself by rename, keeping the previous build as `.old`. HTTPS and GitHub hosts only; a checksum mismatch aborts. The CLI applies the update after the conversion it was asked for; the GUI restarts into it only while the window is untouched. Opt out with `--no-update`, `DECCAN_CONVERT_NO_UPDATE=1`, or a `.no-auto-update` marker beside the binary.

Reaching 1.1.0 requires one manual download — 1.0.x has no updater. Every release after it installs itself.

## 1.0.2 — 1 August 2026

Bundled kit refreshed with the light-only rendering contract and the restored body gutter.

## 1.0.1 — 23 July 2026

Hardening against untrusted input documents; Windows SmartScreen guidance expanded.

## 1.0.0 — 23 July 2026

First release: converts `.md`, HTML, `.docx`, `.xlsx`, `.pptx`, and PDF into deccan-design artifacts, with print-contract verification on every PDF and `--export-kit` for offline endpoints.
