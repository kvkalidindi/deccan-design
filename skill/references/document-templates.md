# Document templates

This skill ships an HTML slot-fill template in `assets/templates/document.html`. The repository also ships native Office and Google Workspace templates in the parent `templates/` tree — pointers below.

## HTML slot-fill template

`assets/templates/document.html` is the canonical template for HTML / PDF documents. Eight slots:

| Slot | Type | Use |
|---|---|---|
| `{{TITLE}}` | string | Cover and document title. Max 22 ch on the cover. |
| `{{SUBTITLE}}` | string | Cover subtitle. Max 50 ch. Optional. |
| `{{DOCUMENT_TYPE}}` | string | Cover eyebrow chip — "Standard", "Specification", "Policy", "Memo", "Brief", "Report", "Letter", "Proposal". |
| `{{PREPARED_BY}}` | string | Cover author line. Office, team, or named individual. |
| `{{DATE}}` | string | Cover date. Format: "May 2026" or "14 May 2026". |
| `{{VERSION}}` | string | Cover version. Format: "1.0", "2.1.3". |
| `{{CLASSIFICATION}}` | one of: Public, Internal, Confidential, Restricted | Cover classification chip. |
| `{{BODY_HTML}}` | HTML | Full document body. Multiple `<section class="section">` blocks, each with its own H1. The body is responsible for its own structure within the system. |

Fill the slots; do not rewrite the surrounding CSS or HTML structure. The template is the contract.

The slot reference also lives in `assets/templates/document-slots.md`.

## Native Office templates

Under `templates/` in the repository root, not under this skill:

| Application | Template family | Path |
|---|---|---|
| Word | Generic document | `templates/word/deccan-document.dotx` |
| Word | Technical spec | `templates/word/deccan-technical-spec.dotx` |
| Word | Policy | `templates/word/deccan-policy.dotx` |
| Word | Customer letter | `templates/word/deccan-customer-letter.dotx` |
| Excel | Generic workbook | `templates/excel/deccan-workbook.xltx` |
| Excel | Comparison grid | `templates/excel/deccan-comparison.xltx` |
| Excel | Financial model | `templates/excel/deccan-financial-model.xltx` |
| PowerPoint | Generic deck | `templates/powerpoint/deccan-deck.potx` |
| PowerPoint | Customer pitch | `templates/powerpoint/deccan-customer-pitch.potx` |
| PowerPoint | Internal review | `templates/powerpoint/deccan-internal-review.potx` |
| Outlook | Signature (HTML) | `templates/outlook/deccan-signature.htm` |
| Outlook | Signature (plain) | `templates/outlook/deccan-signature.txt` |

All native templates carry the deccan-design v2.0 styles. Heading 1 has `pageBreakBefore`. Three sections per Word template (cover / body / end) for footer suppression. PowerPoint masters are wide-format (`LAYOUT_WIDE`, 13.33 × 7.5").

## Google Workspace templates

Under `templates/gworkspace/`:

| File | Use |
|---|---|
| `deccan-document-for-drive.docx` | Upload + open with Google Docs. |
| `deccan-workbook-for-drive.xlsx` | Upload + open with Google Sheets. |
| `deccan-deck-for-drive.pptx` | Upload + open with Google Slides. |
| `deccan-gmail-signature.html` | Paste into Gmail Settings → General → Signature. |

Workflow: upload to Drive, right-click → Open with → Docs / Sheets / Slides, then File → Save as Google Docs / Sheets / Slides.

For Workspace admins: bulk import via Admin Console's Template Gallery is supported. The README at `templates/gworkspace/README.md` documents the procedure.

## Choosing a template

Heuristics for the AI:

- A user asks for a "memo", "status update", "policy", or "internal document" → `deccan-document.dotx` or the HTML slot template.
- A user asks for a "technical specification", "spec", "engineering doc" → `deccan-technical-spec.dotx`.
- A user asks for a "policy", "procedure", "compliance document" → `deccan-policy.dotx`.
- A user asks for a "customer letter", "letter to a customer", "external letter" → `deccan-customer-letter.dotx`.
- A user asks for a "workbook", "spreadsheet", "table" → `deccan-workbook.xltx`.
- A user asks for a "comparison", "decision matrix", "weighted scoring" → `deccan-comparison.xltx`.
- A user asks for a "financial model", "three-statement model", "P&L forecast" → `deccan-financial-model.xltx`.
- A user asks for a "deck", "presentation", "slides" → `deccan-deck.potx`.
- A user asks for a "customer pitch" or "external presentation" → `deccan-customer-pitch.potx`.
- A user asks for an "internal review", "monthly review" → `deccan-internal-review.potx`.

If the user asks for the output as HTML, fill the slot template directly. If the user asks for DOCX / XLSX / PPTX, do not invoke COM automation on the corporate Windows machine — produce the file via python-docx / openpyxl / python-pptx, or point the user at the native template and ask them to fill it in Office.

## Fonts in the templates

The Office templates use Segoe UI Variable / Cascadia Mono by reference. They do not embed font binaries. On Windows 11 the chains resolve to the resident faces. On Windows 10 the static Segoe UI faces are metric-compatible.

## What not to do

- Do not modify the template structure on a per-document basis. The template is the contract.
- Do not rewrite the CSS to switch fonts, colours, or page furniture. If a change is needed, it goes into the system, not the document.
- Do not embed third-party fonts in a Deccan document. The OS-native chain is the policy.
- Do not introduce a per-document `@page` override. The system carries one.
