# Google Workspace templates — usage

Four files in this directory mirror the native Office templates for use in Google Workspace.

| File | Use |
|---|---|
| `deccan-document-for-drive.docx` | Document template |
| `deccan-workbook-for-drive.xlsx` | Workbook template |
| `deccan-deck-for-drive.pptx` | Presentation template |
| `deccan-gmail-signature.html` | Gmail signature snippet |

## Per-user workflow

1. Upload the relevant file (`.docx`, `.xlsx`, or `.pptx`) to Google Drive.
2. Right-click → **Open with** → **Google Docs / Sheets / Slides** depending on the file type.
3. In the opened editor: **File → Save as Google Docs / Sheets / Slides**. The file is now a native Workspace document on the deccan-design template.
4. Optional: move the saved file into a `Templates/` folder in My Drive for reuse.

The conversion preserves the colour tokens, type tokens, named styles, and page furniture. Google's rendering substitutes Segoe UI Variable with its nearest match if the user does not have the font available; on Windows 11 the resident face wins.

## Workspace-admin workflow (bulk import)

For organisation-wide template availability:

1. Sign in to the Google Workspace **Admin Console** as a super-administrator.
2. Apps → Google Workspace → Drive and Docs → Templates.
3. Enable the Template Gallery for the relevant OUs.
4. From a shared "Deccan Templates" folder, submit each `.docx` / `.xlsx` / `.pptx` to the Template Gallery under a "Deccan Fine Chemicals" category.
5. Users can now create new documents via **Google Docs → New → From a template → Deccan Fine Chemicals**.

## Gmail signature

1. Open Gmail → Settings (gear icon) → **See all settings**.
2. **General** tab → **Signature** → **Create new**.
3. Name the signature "Deccan".
4. In the signature editor, paste the rendered HTML from `deccan-gmail-signature.html` after substituting `{{NAME}}`, `{{ROLE}}`, `{{EMAIL}}`, and `{{PHONE}}` with your details.
5. Set the signature defaults: "For new emails use:" and "On reply/forward use:" to **Deccan**.
6. Save changes.

Gmail's compose window renders the HTML signature inline. Because the signature uses inline styles only (no `<style>` block), Gmail preserves all formatting across web, mobile, and Workspace-on-iOS / Android.

## What this directory does not contain

- No `.dotx` / `.xltx` / `.potx` mirrors. Google Workspace does not consume Office template content types; the `.docx` / `.xlsx` / `.pptx` variants serve both purposes.
- No PDF. PDF is produced on demand from the Workspace UI's **File → Download → PDF**.
