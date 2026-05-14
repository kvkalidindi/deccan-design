# Logo usage

## Clear space

The Deccan Fine Chemicals wordmark carries a minimum of **0.5× its own height** as clear space on all sides. No element — type, rule, image, paper edge — enters the clear space.

## Minimum size

- **Print:** 12 mm wide minimum.
- **Screen:** 80 px wide minimum.

Below these thresholds the wordmark loses legibility on standard corporate output devices.

## Colour variants

| Variant | Use |
|---|---|
| Full colour (Deccan Blue rule + Deccan Green dot + stone-900 text) | Default for paper backgrounds in colour print and on-screen. |
| Monochrome black on paper | Single-colour print contexts — faxes, low-end printers, plain-paper photocopies. |
| Monochrome white on Deccan Blue | Single-colour print on dark stock; cover-variant reverse. |
| Sustainability context (full colour, Deccan Green retained) | BRSR / ESG / sustainability content per §04 of the spec. |

## Banned uses

- Rotating, skewing, or distorting the wordmark.
- Recolouring the rule or text to any colour other than the authorised variants.
- Placing the wordmark over photographic backgrounds where contrast falls below WCAG AA.
- Adding drop shadows, glows, bevels, or other ornament.
- Rendering the wordmark in a face other than Segoe UI Variable / Segoe UI semibold.
- Cropping or partially obscuring the wordmark.

## Assets and retrieval

Wordmark assets live in `skill/assets/`:

- `logo.svg` — vector wordmark (preferred for print and high-DPI screen).
- `logo.png` — 1024×1024 raster fallback.
- `logo.b64.txt` — base64-encoded PNG for inline embedding in HTML.

Retrieval cascade (first source wins):

1. Bundled skill asset (`skill/assets/logo.{svg,png}`).
2. Project file (whatever the document's working directory ships).
3. Stable raw GitHub URL `https://raw.githubusercontent.com/kvkalidindi/deccan-design/main/skill/assets/logo.png`.
4. Base64 fallback (`skill/assets/logo.b64.txt`).

The wordmark is **not** fetched from `deccanchemicals.com` — the marketing-site asset is not authoritative for system use.
