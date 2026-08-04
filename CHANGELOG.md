# Changelog

Package releases of the deccan-design system. The **design system itself is v2.0** — its rules (tokens, type stack, grid, the eight document-furniture rules) have not changed. Package versions carry the skill, the templates, and the tooling that delivers them.

Two release lines share this repository:

- `v*` — the design system: skill bundle and templates bundle, built by `release-design-system.yml`.
- `converter-v*` — Deccan Convert, the document converter binary, built by `release-converter.yml`.

---

## v2.3.1 — 4 August 2026

**A fetch answered by a cache no longer masquerades as current.** In-progress conversations were regenerating documents from an old template revision even after a newer release, on every surface. Three gaps let this persist through v2.0.3 (revision markers), v2.2.0 (fetch-every-time), and v2.3.0 alike: the canonical URL is byte-identical on every request, so the CDN (`cache-control: max-age=300`), the fetch infrastructure, and the conversation's own earlier fetch result can all satisfy the mandated fetch with a stale body — a cache hit *is* a fetch under the old wording; the session-side self-checks tested marker *presence*, which every revision since 2.0.3 passes, never *recency*; and "a template held in conversation context" read as banning pasted or prior-document copies, so a session reasonably reused the copy it had itself fetched at the start of a long conversation.

The rule now closes all three: every fetch carries a **unique cache-busting query string** (`?fetch=<unique value>` — the server ignores it, caches key on it, so the request goes end to end); the fetch is **per document build**, not per conversation — regenerations, retries, and revisions each refetch, and a copy fetched earlier in the same session is explicitly conversation context; and the bundled copy's revision is a **freshness floor** — a fetched revision older than the bundle proves a cache answered, forcing one refetch and then a declared fallback to the bundle. The same directive is carried in the workspace instructions, the personal preferences block, the slots reference, and the template's own header. The release build fails if the unique-query directive, the per-build rule, the freshness floor, or the template header note is dropped.

## v2.3.0 — 4 August 2026

**Research reports are a first-class document type.** `SKILL.md` § "Research reports" defines the deliverable: HTML output by default, Word `.docx` only when the user chooses it (printable to PDF from Word), and a mandatory table of contents in which **every entry hyperlinks to its section** — anchor links to stable section ids in HTML, a real `TOC \o "1-3" \h` field in Word. The slot template now styles linked TOC entries (`.toc li a`, ink at rest, accent on hover) and the components reference carries the linked-TOC markup. Light-only remains the hard default; a dark variant is produced only on the user's explicit request, screen-only, with print kept pure white. The release build fails if the section, the HTML-by-default rule, the hyperlinked-TOC field, the light-only default, or the linked-TOC styling is dropped.

**The attribution default is the Deccan IT and Digital Transformation Team.** Rules 1–2 of the resolution order are unchanged (stated author, then the requesting user's session identity). Rule 3 no longer stalls on a question: when no author resolves, the document is attributed to "Deccan IT and Digital Transformation Team" and the response says the default was applied. Personal names, office titles, and account slugs that identified the design-system maintainer were removed from every layer — the skill, the slot reference, the plugin and marketplace manifests, the README, the copyright notice, the admin guide and verification prompt, the spec and specimen covers, and the policy template's sample content and document metadata. Repository provenance remains prohibited evidence of authorship; the release gates now check for the provenance ban and the team default instead of a literal slug.

**Legacy design-system names retired from the record.** Every reference to the pre-2.0 design systems by name is gone from the skill, the README, the spec, the specimen, the admin guide, the instruction blocks, and the asset headers. Supersession language is generic — "every earlier Deccan design system" — so the override no longer depends on remembering what the old systems were called.

## v2.2.0 — 1 August 2026

**Fetching the canonical template is now a hard rule.** The previous rule was conditional — fetch *if the session can*, otherwise use the bundled copy silently — which left the cheapest path (use what is already loaded) available and undetectable. An installed bundle lags the repository as a matter of course, so that path produced documents built from whatever template happened to be frozen into the bundle at install time.

The rule is now unconditional: fetch the canonical template at build time, every time, before filling a slot, and fill the copy that comes back. The bundled copy is a fallback for a session with no network and nothing else, and a session that falls back must say so in its response — naming the revision used and that it may lag. A template held in conversation context or lifted from a previous document is never acceptable.

**The rendering invariant makes the outcome checkable.** Before returning any HTML the session confirms the output carries the generator meta, the `color-scheme` meta, `color-scheme: light only`, the pinned `:root` canvas rule, and the dark-mode block. Any one missing means the document renders dark-on-dark on iOS and Android, so it is rebuilt rather than returned. This is a property of the artifact, independent of which template the session thought it used.

Both rules are stated at every layer that reaches a surface — the skill, the workspace instructions, and the personal preferences block — and the release build fails if the skill drops either section, the fetch-first directive, or any marker from the invariant. The converter suite additionally asserts that the offline kit ships both rules and a render-safe template.

## v2.1.3 — 1 August 2026

**A revised document no longer inherits the old stylesheet.** A v2.0 of a brief first issued in July came out rendering dark-on-dark despite every surface being current. The artifact carried no `color-scheme`, no revision marker, no generator meta and the zero-gutter `main.body` rule — it was the 14 May template verbatim. The skill was not at fault and was demonstrably loaded: the document carries all nine audit-grade elements that shipped hours earlier in v2.1.2. What happened is that the session built the new version from the *previous version of the document* and reused its `<style>` block, so the template was never opened and no template-side fix could apply.

`SKILL.md` § "Revising an existing document" now states the rule: content carries forward, presentation never does — never copy the prior version's stylesheet, head, cover, or end page. It adds a self-check with a single observable: the output must contain the `<meta name="generator">` line, whose absence proves the template was not used. The release build fails if either the section or the self-check is dropped.

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

**A finished render no longer dies cleaning up its own log.** The browser's stdout was redirected into a file inside the browser's own profile directory; helper processes inherit that handle and outlive the parent, so temp-directory cleanup tried to delete a file still held open — a hard `PermissionError` on Windows, raised *after* the PDF was written. The log now gets its own directory and both are cleaned leniently.

**Self-update on launch.** The binary had no update path, so an endpoint kept whatever build it first downloaded — including the design kit frozen inside it. It now checks the pinned repository's `converter-v*` releases at most once a day, verifies the artifact against the SHA-256 in that release's own `SHA256SUMS.txt`, and swaps itself by rename, keeping the previous build as `.old`. HTTPS and GitHub hosts only; a checksum mismatch aborts. The CLI applies the update after the conversion it was asked for; the GUI restarts into it only while the window is untouched. Opt out with `--no-update`, `DECCAN_CONVERT_NO_UPDATE=1`, or a `.no-auto-update` marker beside the binary.

Reaching 1.1.0 requires one manual download — 1.0.x has no updater. Every release after it installs itself.

## 1.0.2 — 1 August 2026

Bundled kit refreshed with the light-only rendering contract and the restored body gutter.

## 1.0.1 — 23 July 2026

Hardening against untrusted input documents; Windows SmartScreen guidance expanded.

## 1.0.0 — 23 July 2026

First release: converts `.md`, HTML, `.docx`, `.xlsx`, `.pptx`, and PDF into deccan-design artifacts, with print-contract verification on every PDF and `--export-kit` for offline endpoints.
