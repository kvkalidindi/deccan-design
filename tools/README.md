# tools/

Build and QA helpers for the deccan-design system. **Not part of the installer payload.** These scripts are for developers and QA working on the design system itself, not for end-user endpoints.

| Script | Use |
|---|---|
| `Render-DeccanDocumentPdf.ps1` | Render an HTML deliverable to PDF via Edge or Chrome headless, then optionally verify the page structure (cover with no footer, body pages with footers, end page with no footer). |

## Render-DeccanDocumentPdf.ps1

The deccan-design CSS encodes a strict print contract. This script renders any HTML deliverable (the spec, the specimen, the admin guide, the slot-template fill, or any custom document) to PDF and checks each page against the contract — without bouncing through the Office or browser UI.

### Quick start

```powershell
# Render a memo to PDF
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\my-memo.html

# Render and verify the page structure
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\my-memo.html -Verify

# Render, verify, and open the result in the default viewer
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\my-memo.html -Verify -OpenAfter

# Use Chrome instead of Edge
.\tools\Render-DeccanDocumentPdf.ps1 .\path\to\my-memo.html -Browser chrome
```

### What `-Verify` checks

For each page:

- **Cover (page 1):** must NOT have the running footer (`Deccan Fine Chemicals · Confidential <N>`).
- **Body pages (2 through N-1):** must have the running footer.
- **End page (page N):** must NOT have the running footer.

Any deviation prints a `[FAIL]` line and the script exits non-zero — useful for CI guard-rails on documents generated from the slot template.

### Prerequisites

- Microsoft Edge or Google Chrome installed (default locations).
- `pdftotext.exe` for `-Verify`. Ships with Git for Windows at `C:\Program Files\Git\mingw64\bin\pdftotext.exe`. If absent, `-Verify` is skipped with a warning.

### Why this helper exists

The deccan-design print contract has three failure modes that don't surface until a document is rendered to a paged medium:

1. `min-height: 100vh` overflows the live content area, splitting the cover.
2. Grid 1fr-row collapse plus `align-self: center` puts content outside the engine's section boundary.
3. `h1.cover-title` inheriting `page-break-before: always` from the global H1 rule pushes the title onto page 2.

A round-trip through "open in Edge → Ctrl+P → Save as PDF → eyeball" is slow. This script collapses that loop to one command and an exit code.
