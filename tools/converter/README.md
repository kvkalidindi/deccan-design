# Deccan Convert

A user-space utility for Windows 11 and macOS that converts documents into deccan-design v2.0 artifacts. Runs without administrator rights. Double-click for the GUI; pass arguments for the CLI.

Downloads: the [GitHub releases page](https://github.com/kvkalidindi/deccan-design/releases) carries `deccan-convert-windows-x64.exe` and `deccan-convert-macos-arm64.zip` (a `Deccan Convert.app` bundle) for tags named `converter-v*`.

## What it does

Takes an artifact in any supported format and produces a version rendered under the deccan-design principles — OS-native type stack, Deccan Blue single accent, stone neutrals, audit-grade document furniture, and the print contract (cover and end pages without footers, body pages with the running footer and bare page numbers).

## Supported conversions

Documents (md / html / docx / pdf) convert freely between document formats. Spreadsheets and decks restyle to their own format — data and formulas are never altered, only presentation.

| in \ out | md | html | docx | pdf | xlsx | pptx |
|---|---|---|---|---|---|---|
| **md**   | — | ✓ | ✓ | ✓ | — | — |
| **html** | ✓ | ✓ | ✓ | ✓ | — | — |
| **docx** | ✓ | ✓ | ✓ | ✓ | — | — |
| **pdf**  | ✓\* | ✓\* | ✓\* | — | — | — |
| **xlsx** | — | — | — | — | ✓ | — |
| **pptx** | — | — | — | — | — | ✓ |

\* PDF input is text extraction only: no OCR, images are dropped, multi-column layouts may interleave. Use it to rescue content into the design system, not to round-trip.

Deliberate gaps, and what to do instead:

- **xlsx / pptx → PDF:** restyle first, open the result in Excel / PowerPoint, then File → Export → Create PDF/XPS. The design-system print policy forbids automated Office rendering (COM automation hangs on Trust Center dialogs on the corporate fleet).
- **HTML → PDF requires a browser:** the PDF writer prints through headless Microsoft Edge, Google Chrome, or Chromium — whichever is installed, including per-user installs. If none is found, the styled HTML is saved next to the requested output with instructions instead.

## Google Workspace (Docs / Sheets / Slides)

Google files are not local files, so the flow is export → convert → re-upload:

1. In Google Docs / Sheets / Slides: **File → Download** → Microsoft Word / Excel / PowerPoint.
2. Convert the downloaded file with Deccan Convert.
3. Upload the result to Drive and **Open with Google Docs / Sheets / Slides → File → Save as Google …**.

This mirrors the `templates/gworkspace/` workflow and needs no Google account setup.

## GUI

Launch with no arguments (double-click). Pick the input file; the output-format list shows only valid targets for that input. For document formats, the details panel pre-fills from the file's own metadata (front matter, Word properties, PDF info) — title, document type, and prepared-by are required and never invented, so fill in whatever could not be extracted. Warnings (PDF fidelity, dropped charts) and the print-contract verification result appear in the status log.

## CLI

```
deccan-convert INPUT (-o OUTPUT | --to FORMAT)
               [--title T] [--subtitle S] [--type Report] [--prepared-by WHO]
               [--date "July 2026"] [--version 1.0] [--classification Internal]
               [--template document|technical-spec|policy|customer-letter]
               [--logo] [--no-verify] [--no-update]
deccan-convert --export-kit DIR
deccan-convert --check-update
```

Examples:

```bash
# Word report to a print-contract-verified PDF
deccan-convert q2-report.docx -o q2-report.pdf --classification Internal

# Markdown (front matter carries the metadata) to Word
deccan-convert audit.md --to docx

# Restyle a Google Sheets export; writes book-deccan.xlsx next to the input
deccan-convert book.xlsx --to xlsx
```

Exit codes: `0` success · `1` unexpected error · `2` unsupported conversion or bad input · `3` PDF written but the print-contract verification failed.

On the Windows build (a windowed app), CLI output is also written to `<output>.log` beside the converted file when no console is attached.

Every PDF the tool produces is verified against the print contract automatically (cover page 1 without footer, body pages with the running footer, end page without footer) — the same check `tools/Render-DeccanDocumentPdf.ps1 -Verify` performs, with no external dependencies. `--no-verify` skips it.

## Template flavors (`--template`, Word output only)

Word output can inherit any of the four Word template families: `document` (default), `technical-spec`, `policy`, `customer-letter`. Selecting a flavor also implies its default document type (Specification / Policy / Letter) when the input carries none. The flavor option applies to `.docx` output only — HTML/PDF flow through the single canonical slot template, and spreadsheets/decks have exactly one design by construction (the restyle track preserves the source's structure and applies the one token recipe).

## Logo option (`--logo`)

By default covers carry the sanctioned *text* wordmark ("Deccan Fine Chemicals" with the blue rule) — resolution- and network-proof. `--logo` (or the GUI checkbox) swaps the cover mark for the graphical Deccan wordmark from the **bundled** asset: embedded as a data URI in HTML/PDF, as an image part in docx/pptx. Nothing is ever fetched; the end page keeps the text mark.

## Export kit — equip any offline endpoint (`--export-kit DIR`)

The binary carries the complete design system, not just what it needs to convert. `deccan-convert --export-kit DIR` writes `DIR/deccan-design-kit/` containing every Office template (4 Word, 3 Excel, 3 PowerPoint), the Google Workspace files, both email signatures, and the Anthropic Claude skill (rules, tokens, print contract, slot template, logo assets), plus a README covering per-user template installation and how to equip a Claude environment offline (copy `skill/` to `<repo>/.claude/skills/deccan-design/`). One downloaded binary makes any machine a fully-equipped deccan-design endpoint — no repo checkout, no network, no admin rights.

## Automatic updates

The binary keeps itself current. On every launch it checks the repository's
`converter-v*` releases (at most once every 24 hours), and when a newer build
exists it downloads the artifact for this platform, verifies it against the
SHA-256 in that release's `SHA256SUMS.txt`, and swaps it into place. This
matters beyond the converter's own code: the design kit — slot template,
tokens, Office templates, Claude skill — is frozen inside the binary, so a
build that never updates keeps producing documents from a superseded system.

What it will not do:

- **Interrupt work.** The CLI applies the new build after the conversion it
  was asked for, and reports `updated to X — takes effect on the next run`.
  The GUI restarts into the new build only if the window is still untouched;
  once a file is selected the swap waits for the next launch.
- **Run downloaded code.** The verified artifact replaces the installed one
  on disk; it executes only when the app is launched again.
- **Fail loudly.** An offline endpoint, a TLS-intercepting proxy, or a
  GitHub rate limit ends the check silently. Conversions are unaffected.
- **Widen its reach.** HTTPS only, GitHub hosts only, the pinned repository
  only, and only the exact release artifact names. A checksum mismatch
  aborts and leaves the installed build alone.

The previous build is kept beside the new one as `.old` and removed on the
following launch, so a bad update can be rolled back by hand.

Force a check with `deccan-convert --check-update` (installs and exits).

Reaching 1.1.0 takes one manual download — 1.0.x predates the updater and cannot pull itself forward. Every release after it installs itself.

### Turning it off

| Method | Scope | Use for |
|---|---|---|
| `--no-update` | one invocation | scripts and CI that must not touch the network |
| `DECCAN_CONVERT_NO_UPDATE=1` | user or machine, via environment | locked-down profiles |
| `.no-auto-update` file beside the binary | that installation | fleets where Intune / Jamf owns the version |

Updates also switch themselves off when the install directory is not
writable — the managed-install case — and when running from source.

## Document metadata

The document track fills the eight slots of `skill/assets/templates/document.html`. Metadata is discovered in this order: user-provided values (GUI fields / CLI flags) win, then values extracted from the input (markdown front matter, Word core properties, PDF document info, deccan HTML cover), then the documented defaults (version `1.0`, date = current month, classification `Confidential`). Title, document type, and prepared-by have no defaults — per the slot policy they are never invented.

Markdown front matter keys: `title`, `subtitle`, `type`, `author`, `date`, `version`, `classification`.

## The binaries are unsigned (by design)

Same policy as the MSI/PKG installers (admin guide, PRD §1.4 Decision 5). The binaries carry no code-signing certificate, so SmartScreen and Gatekeeper flag them as from an unknown publisher with no download reputation — this is expected, not a fault in the file. Verify the SHA256 and proceed.

### Windows — the download and the first run each warn once

1. **Edge download** shows *"deccan-convert-windows-x64.exe isn't commonly downloaded"*. Click the **⋯** on that download entry → **Keep** → **Keep anyway**. (Chrome shows a **▲** → **Keep**.)
2. **On first launch**, SmartScreen shows *"Windows protected your PC"* with only a **Don't run** button visible. Click the **More info** link — a **Run anyway** button appears. Click it. (SmartScreen remembers the choice; it won't prompt again for that copy.)
3. **To avoid the prompt entirely**, clear the mark-of-the-web before launching, in PowerShell:

   ```powershell
   Unblock-File .\deccan-convert-windows-x64.exe
   ```

4. **Verify the download** matches the release build:

   ```powershell
   Get-FileHash .\deccan-convert-windows-x64.exe -Algorithm SHA256
   ```

   Compare the hash against `SHA256SUMS.txt` on the release page.

### macOS — Gatekeeper

Unzip, then right-click `Deccan Convert.app` → **Open** → **Open** on first launch (or System Settings → Privacy & Security → **Open Anyway**). Verify with `shasum -a 256 deccan-convert-macos-arm64.zip`.

### Managed fleet (no prompts)

Deploy via Microsoft Intune, ManageEngine Endpoint Central, or Jamf. MDM-deployed apps bypass SmartScreen / Gatekeeper entirely, and IT can whitelist the release SHA256 for reputation. This is the sanctioned path for wide rollout; the per-user download warnings above only affect people downloading the binary directly from GitHub.

Checksums for every release are in the attached `SHA256SUMS.txt`.

## Development

```bash
cd tools/converter
pip install -e '.[test]'
python sync_assets.py          # populate deccan_convert/assets_data/ from the repo sources
python -m pytest tests/ -q     # unit tests; browser-dependent tests auto-skip
python -m deccan_convert sample.md -o sample.pdf   # run from source
```

Design assets are bundled copies of the repository's single sources of truth (`skill/assets/templates/document.html`, the logo, and the Office templates). `sync_assets.py --check` fails CI when the copies drift. `deccan-document-base.docx` is generated from `templates/word/deccan-document.dotx` by swapping the OOXML content type, because python-docx opens documents, not templates — the styles, theme, page setup, and footer contract carry over verbatim.

Builds run in `.github/workflows/release-converter.yml`: unit tests on Ubuntu, PyInstaller builds on `windows-latest` and `macos-latest`, an end-to-end md→PDF smoke test with print-contract verification on both, and a GitHub Release on `converter-v*` tags.

### Constraints inherited from the design system

- **No Office COM automation** — restyling uses python-docx / openpyxl / python-pptx only.
- **No font embedding** — typefaces are referenced by name; the OS-native chains resolve them.
- **PDF via browser headless print only**, per the print policy.

### Security posture (untrusted input)

The converter treats every input document as untrusted. Hardening applied (see `deccan_convert/limits.py` and `tests/test_security.py`):

- **No render-time network access.** The HTML sanitizer drops all remote and `file:` image references (only inline `data:image/` survives) and scheme-allow-lists links, so a converted document cannot beacon out, reach internal hosts (SSRF), or probe the local filesystem. The headless PDF render additionally runs with all DNS blackholed (`--host-resolver-rules=MAP * ~NOTFOUND`) as defense-in-depth, and the Chromium sandbox stays on (the `--no-sandbox` retry is opt-in via `DECCAN_CONVERT_ALLOW_NO_SANDBOX=1`, for root/CI only).
- **Resource-exhaustion guards.** Inputs over 100 MB are rejected; Office files are checked for zip-bomb decompression (per-entry size, total size, ratio, entry count) before opening; a DTD/entity declaration in `word/document.xml` is rejected (blocks mammoth billion-laughs expansion); spreadsheet styling is capped to a sane row/column region; PDF parsing is page-capped; and data-URI images are size-bounded before decode.
- **XXE is not exploitable** — python-docx, openpyxl, and python-pptx all parse with external-entity resolution disabled.
- **No source overwrite.** The input-equals-output guard uses filesystem identity (`os.path.samefile`), which also catches case-insensitive filesystems.
- HTML metadata is HTML-escaped; `<script>`/`<style>`/`<svg>`/`<iframe>` and inline `style` attributes are stripped with content.
