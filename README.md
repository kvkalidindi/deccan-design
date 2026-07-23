# deccan-design

The corporate design system of Deccan Fine Chemicals. Documents, slide decks, web pages, UI mockups, brand artifacts, and email signatures produced under this system conform to one rule set: OS-native type stack, single Deccan Blue accent, 12-column 8-pixel grid, no rounded structural corners, corporate tone of voice, and audit-grade document furniture.

Version 2.0 — May 2026.

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
| [`claude/`](claude/) | The personal-preferences text users paste into Claude.ai → Settings → Profile → Preferences. |

## Install

The current release is **v2.0.0**. Download the installer for your platform from the [GitHub release page](https://github.com/kvkalidindi/deccan-design/releases/tag/v2.0.0):

- **Windows:** `deccan-design-2.0.0.msi`
- **macOS:** `deccan-design-2.0.0.pkg`
- **All templates as a zip:** `templates-bundle.zip`

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
| Ask Claude for a Deccan document | In any Claude surface, ask: *"Generate a one-page Deccan status memo about &lt;topic&gt;."* The `deccan-design` skill activates automatically once installed. |

## Deccan Convert — apply the system to existing documents

**Deccan Convert** is a downloadable utility for Windows 11 and macOS that takes an existing artifact — `.md`, HTML, Word `.docx`, Excel `.xlsx`, PowerPoint `.pptx`, PDF, or a Google Docs / Sheets / Slides export — and produces a version rendered under the deccan-design principles, in your choice of supported output format. It runs entirely in user space; no admin rights needed.

- **Download:** `deccan-convert-windows-x64.exe` or `deccan-convert-macos-arm64.zip` from the [releases page](https://github.com/kvkalidindi/deccan-design/releases) (tags named `converter-v*`). Like the installers, the binaries are **unsigned by design** — the same SmartScreen / Gatekeeper steps above apply.
- **Use:** double-click for the GUI, or script it: `deccan-convert report.docx -o report.pdf --classification Internal`. Word output can target any template family (`--template policy`), and `--logo` puts the graphical wordmark on the cover (bundled asset — nothing fetched).
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

- `swiss_design_at_deccan` v1 (IBM Plex stack) and v2 (OS-native, renamed under this project).
- `deccan-design v1.0` (the deferred Aptos plan).
- Any inherited preference for IBM Plex Sans/Mono, Hanken Grotesk, Fira Code, Aptos, Inter, or any "Deccan default" referenced in older personal-preference blocks or memory.

The override is documented in [`claude/personal-preferences.md`](claude/personal-preferences.md) and in `skill/SKILL.md`.

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
| Eight document-furniture rules | See spec §07 and `docs/references/document-furniture.md` |

## License

This repository is **fully owned by Deccan Fine Chemicals Pvt. Ltd.** It is published publicly for informational reference. **No license to use, copy, modify, or distribute** any content is granted. See [`COPYRIGHT.md`](COPYRIGHT.md).

## Contact

Issues with the system itself: open the admin guide's escalation matrix to find the appropriate tier.

For commercial inquiries about Deccan Fine Chemicals: <https://www.deccanchemicals.com>.

---

*deccan-design v2.0 · Office of the SVP, IT &amp; Digital Transformation · Deccan Fine Chemicals Pvt. Ltd. · May 2026.*
