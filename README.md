# deccan-design

The corporate design system of Deccan Fine Chemicals. Documents, slide decks, web pages, UI mockups, brand artifacts, and email signatures produced under this system conform to one rule set: OS-native type stack, single Deccan Blue accent, 12-column 8-pixel grid, no rounded structural corners, corporate tone of voice, and audit-grade document furniture.

Design system **v2.0** · current package release **v2.4.0** (August 2026). The system version moves when the rules change; package releases carry the skill, templates, and tooling. History: [`CHANGELOG.md`](CHANGELOG.md). A CI release gate keeps `main` identical to the latest release, so the canonical raw URLs on `main` always serve the released content.

## What is in this repository

| Folder | What it contains |
|---|---|
| [`docs/spec/`](docs/spec/) | The authoritative system specification (HTML). |
| [`docs/specimen/`](docs/specimen/) | Plate-by-plate visual demonstration of each rule. |
| [`docs/admin-guide/`](docs/admin-guide/) | IT operations rollout, deployment, and support reference. |
| [`docs/references/`](docs/references/) | Token, type, logo, and document-furniture references. |
| [`skill/`](skill/) | The Anthropic skill module for Claude Code / Claude Desktop / Claude.ai. |
| [`templates/`](templates/) | Native Office (Word / Excel / PowerPoint), Outlook signature, and Google Workspace templates. |
| [`installers/`](installers/) | Windows MSI (WiX v4) and macOS PKG (pkgbuild / productbuild). Both **unsigned**. |
| [`tools/converter/`](tools/converter/) | **Deccan Convert** — the document converter utility for Windows 11 / macOS (source + build). |
| [`claude/`](claude/) | The instruction blocks pasted into Claude.ai: `workspace-instructions.md` (admins → Workspace → Custom instructions, org-wide) and `personal-preferences.md` (each user → Profile → Preferences). |
| [`plugin/`](plugin/) + [`.claude-plugin/`](.claude-plugin/) | Claude Code plugin and marketplace manifest. The skill tree is mirrored under `plugin/skills/`; CI gates the mirror against `skill/`. |
| [`tools/release/`](tools/release/) | `build_bundles.py` — builds the release bundles and enforces the frontmatter, revision-marker, attribution, and plugin-mirror gates. |

## Install

The current design-system release is **v2.4.0** — [latest release](https://github.com/kvkalidindi/deccan-design/releases/latest):

- **Claude Code (recommended):** the repo is a plugin marketplace — one-time setup, automatic updates from `main` afterwards:

  ```
  claude plugin marketplace add kvkalidindi/deccan-design
  claude plugin install deccan-design@deccan
  ```

- **Claude.ai workspace (admins):** upload `deccan-design-skill-bundle.zip` via Settings → Workspace → Skills; paste `claude/workspace-instructions.md` into Workspace → Custom instructions. Claude Desktop and the mobile apps inherit both automatically. Rollout runbook: `docs/admin-guide/org-rollout.md`.
- **All templates as a zip:** `templates-bundle.zip`

Both bundles are built from the tagged tree by CI, so they carry exactly what is committed.

The MSI / PKG installers remain the channel for the **Office templates and Outlook signature**. Their bundled Claude-skill copy is legacy — Claude Code takes the skill from the plugin marketplace, Claude Desktop from the workspace. The installer definitions track the package version — kept equal to the skill version by `build_bundles.py --sync-versions` and gated by `--check`; they are built on managed endpoints (WiX on Windows, `pkgbuild` on macOS) and attached to the matching release afterwards, so the packages on a given release may lag the bundles on it.

Per-user install. No admin elevation required.

### Important — the installer is unsigned

The MSI and PKG ship **unsigned by design** (see the admin guide for the rationale). On first install:

- **Windows** shows SmartScreen: *"Windows protected your PC."* Click **More info** → **Run anyway**.
- **macOS** shows Gatekeeper: *"cannot be opened because Apple cannot check it for malicious software."* Right-click the `.pkg` → **Open** → confirm. Or System Settings → Privacy &amp; Security → **Open Anyway**.

For silent enterprise deployment via Microsoft Intune, ManageEngine Endpoint Central, or Jamf, the MDM push bypasses these warnings. The admin guide covers this.

### Configure the Outlook signature

The installer drops an unconfigured signature template. Run the helper once to fill in your name, role, email, and phone:

- **Windows:** `& "$env:APPDATA\deccan-design\Set-DeccanSignature.ps1"`
- **macOS:** `~/Library/Application Support/deccan-design/set-deccan-signature.sh`

Then in new Outlook: Settings → Accounts → Signatures → select **Deccan** as the default for new messages and replies / forwards.

### Configure Claude.ai personal preferences

The installer cannot push Claude.ai preferences server-side. Paste the text from [`claude/personal-preferences.md`](claude/personal-preferences.md) into Claude.ai → Settings → Profile → Preferences. One-time per Claude.ai account.

## Quick start

| I want to… | Do this |
|---|---|
| Create a new document | Word → File → New → Personal → pick a `deccan-…` template. |
| Create a new workbook | Excel → File → New → Personal → pick a `deccan-…` template. |
| Create a new deck | PowerPoint → File → New → Personal → pick a `deccan-…` template. |
| Use the system in Google Docs | Upload the `templates/gworkspace/*.docx` → Open with Google Docs → File → Save as Google Docs. |
| Generate an HTML document | Fill the slots in `skill/assets/templates/document.html`. |
| Ask Claude for any document | In any Claude surface, ask: *"Generate a one-page status memo about &lt;topic&gt;."* deccan-design applies by default to any stylized document — the request does not need to mention Deccan — and attributes the document to you. |
| Ask Claude for a research report | *"Generate a research report on &lt;topic&gt;."* The report renders as HTML by default — or Word `.docx` if you ask for it, printable to PDF from Word — with a table of contents whose every entry hyperlinks to its section. Light theme is the hard default; a dark variant is produced only on explicit request. |

## How the system reaches Claude

| Surface | Channel | Updates |
|---|---|---|
| Claude.ai web, Claude Desktop, iOS / Android | Workspace skill + workspace custom instructions (admin-deployed) | Admin re-uploads the bundle per release; a release automatically opens a checklist issue as the reminder |
| Claude Code | Plugin marketplace (`deccan-design@deccan`) | Automatic from `main` after a one-time install |
| Every session, every document | Canonical slot template on `main` | Instant, and mandatory — since v2.2.0 the skill fetches the template at build time on every document and fills the copy that comes back. Since v2.3.1 the fetch is cache-proof: one fetch per document build (regenerations included) with a unique query string, and the fetched revision must not be older than the bundled copy's. Since v2.4.0 a release gate keeps `main` identical to the latest release, so the URL on `main` *is* the latest release. An installed bundle is a no-network fallback that must be declared when used, so a lagging bundle or a stale cache cannot quietly produce a stale document |
| Deccan Convert endpoints | Kit embedded in the binary | Automatic — the binary self-updates from `converter-v*` releases |
| Word / Excel / PowerPoint / Outlook | MSI / PKG | IT rebuild + MDM push. The installers' Claude-skill copy is legacy |

Two behaviours are worth stating plainly because they affect every member:

- **The system is the default**, not an opt-in. Any request for a stylized artifact gets deccan-design whether or not it mentions Deccan — unless the member asks for a different design direction.
- **Documents are attributed to the person who asked for them.** "Prepared by" resolves to a stated author, else the requesting member's identity, else Claude asks — never a silent default, never a name from repository provenance.

- **Templates are fetched, never remembered.** Every HTML document is built from the canonical template pulled at build time — one fetch per document build, carrying a unique cache-busting query string, with the fetched revision checked against the bundled copy's as a freshness floor. The copy inside an installed skill is a fallback for a session with no network, and a session that uses it says so. A template lifted from a previous version of the document — or fetched earlier in the same conversation — is never acceptable.

### The rendering invariant

Documents are previewed against a dark canvas in the Claude iOS and Android apps. A document without the light-only rendering contract shows whole sections as dark text on a dark background — the reader sees blank space. Since v2.2.0 no document leaves the skill without all five of these, checked against the output before it is returned:

```
<meta name="generator" content="deccan-design v2.0 · slot template …">
<meta name="color-scheme" content="light">
color-scheme: light only;
:root { background-color: var(--stone-50) !important; }
@media (prefers-color-scheme: dark) {
```

Any document can be checked in one step: search its source for `generator`. Present means the template was filled and the contract is in place; absent means it was not, whatever else the document contains.

Verification for all four surfaces: [`docs/admin-guide/verification-prompt.md`](docs/admin-guide/verification-prompt.md).

## Deccan Convert — apply the system to existing documents

**Deccan Convert** is a downloadable utility for Windows 11 and macOS that takes an existing artifact — `.md`, HTML, Word `.docx`, Excel `.xlsx`, PowerPoint `.pptx`, PDF, or a Google Docs / Sheets / Slides export — and produces a version rendered under the deccan-design principles, in your choice of supported output format. It runs entirely in user space; no admin rights needed.

- **Download:** `deccan-convert-windows-x64.exe` or `deccan-convert-macos-arm64.zip` from the [releases page](https://github.com/kvkalidindi/deccan-design/releases) (tags named `converter-v*`; current: **1.1.0**). One manual download is needed to reach 1.1.0 — builds at 1.0.x predate the self-updater; every release after it installs itself. Like the installers, the binaries are **unsigned by design** — the same SmartScreen / Gatekeeper steps above apply.
- **Use:** double-click for the GUI, or script it: `deccan-convert report.docx -o report.pdf --classification Internal`. Word output can target any template family (`--template policy`), and `--logo` puts the graphical wordmark on the cover (bundled asset — nothing fetched).
- **Stays current:** the binary checks the `converter-v*` releases on launch (at most daily), verifies the new build against the release checksum, and swaps itself — so the design kit frozen inside it never goes stale. Opt out per run with `--no-update`, per machine with `DECCAN_CONVERT_NO_UPDATE=1`, or per installation with a `.no-auto-update` file beside the binary.
- **Offline design kit:** `deccan-convert --export-kit DIR` writes the complete design system out of the binary — all Office/Workspace templates, signatures, and the Claude skill — so any endpoint is fully equipped with one download, no network or repo checkout needed.
- Documents (md / html / docx / pdf) convert freely between document formats; workbooks and decks restyle in place (data and formulas untouched). Every PDF it produces is verified against the print contract automatically.
- **Google Workspace:** File → Download as docx/xlsx/pptx → convert → re-upload to Drive.

The full manual, support matrix, and format caveats are in [`tools/converter/README.md`](tools/converter/README.md).

## PDF generation — on demand

PDFs are not committed to this repository. The OS-native font stack means sandbox-rendered PDFs would substitute typefaces and confuse readers. Produce a PDF on a managed endpoint where the fonts are resident:

1. **From Word / PowerPoint / Excel:** File → Export → Create PDF/XPS Document. The OS-resident font embeds, producing a faithful PDF.
2. **From HTML:** print to PDF from a modern browser with *Print backgrounds* enabled. Or `wkhtmltopdf document.html document.pdf`.

## What this system supersedes

`deccan-design v2.0` replaces and supersedes all of the following:

- Every earlier Deccan design system, under any earlier name or version.
- `deccan-design v1.0` (the deferred Aptos plan).
- Any inherited preference for IBM Plex Sans/Mono, Hanken Grotesk, Fira Code, Aptos, Inter, or any "Deccan default" referenced in older personal-preference blocks or memory.

The override is documented in [`claude/workspace-instructions.md`](claude/workspace-instructions.md), [`claude/personal-preferences.md`](claude/personal-preferences.md), and `skill/SKILL.md`.

## Specification overview

The complete specification lives in [`docs/spec/deccan-design-spec.html`](docs/spec/deccan-design-spec.html). The cheat-sheet:

| Aspect | Value |
|---|---|
| Sans face | Segoe UI Variable (Windows 11) → Segoe UI (Windows 10) → San Francisco via `system-ui` (macOS) → generic sans-serif |
| Mono face | Cascadia Mono (Windows 11) → Consolas (older Windows) → SF Mono (macOS) → generic monospace |
| Primary accent | `--deccan-blue: #164999` |
| Reserved colour | `--deccan-green: #71BF4D` (logo + sustainability content only) |
| Grid | 12-column, 8 px base, 24 px gutter, 1180 px content max |
| Body size | 17 px screen / 10.5 pt print |
| Print page | Letter, 0.8" outside margins, 1" bottom for footer |
| Colour scheme | Light only — no dark variant; documents pin their canvas so a dark preview host cannot render them dark-on-dark |
| Attribution | "Prepared by" resolves to the requesting user — stated author, else session identity, else ask. Never the system maintainer |
| Eight document-furniture rules | See spec §07 and `docs/references/document-furniture.md` |

## License

This repository is **fully owned by Deccan Fine Chemicals Pvt. Ltd.** It is published publicly for informational reference. **No license to use, copy, modify, or distribute** any content is granted. See [`COPYRIGHT.md`](COPYRIGHT.md).

## Contact

Issues with the system itself: open the admin guide's escalation matrix to find the appropriate tier.

For commercial inquiries about Deccan Fine Chemicals: <https://www.deccanchemicals.com>.

---

*deccan-design v2.0 (package v2.4.0) · Deccan IT and Digital Transformation Team · Deccan Fine Chemicals Pvt. Ltd. · August 2026.*
