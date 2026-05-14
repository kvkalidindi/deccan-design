# Print rules

Print is the high-fidelity end of the medium. The system carries a single `@page` stylesheet that handles every print case: PDF export from a browser, PDF print from Word, and direct browser-to-printer output. Documents do not write per-document print stylesheets — if a rule is needed, it goes into the system.

## Page format

Letter paper, portrait. 0.8-inch outside margins, 1-inch bottom margin to clear the running footer. A4 follows the same proportions and renders without alteration; the live content area scales with the paper.

Live content area on Letter: 6.9" × 9.2".

## `@page` rules — paste verbatim

```css
@page {
  size: Letter;
  margin: 0.8in 0.8in 1in 0.8in;
  @bottom-left {
    content: "Deccan Fine Chemicals · Confidential";
    font-family: 'Cascadia Mono', Consolas, ui-monospace, monospace;
    font-size: 8.5pt;
    color: #78716C;
  }
  @bottom-right {
    content: counter(page);
    font-family: 'Cascadia Mono', Consolas, ui-monospace, monospace;
    font-size: 8.5pt;
    color: #78716C;
  }
}

@page :first {
  @bottom-left  { content: ""; }
  @bottom-right { content: ""; }
}
```

The `@page :first` block suppresses the footer on the cover. The end page is in its own document section with its own footer suppression.

## Running footer

- **Left:** `Deccan Fine Chemicals · Confidential` in Cascadia Mono / Consolas fallback, 8.5 pt, stone-500.
- **Right:** bare integer page number. Mono, 8.5 pt, stone-500. Never `Page X` and never `Page X of Y`.
- **Centre:** empty.

The footer appears only on body pages. Suppressed on the cover and on the end page.

## Page breaks

| Element | Rule |
|---|---|
| H1 | `page-break-before: always` |
| Cover | `page-break-after: always` + `page-break-inside: avoid` |
| End page | `page-break-before: always` + `page-break-inside: avoid` |
| Callout, code block, pull quote, table, TOC | `page-break-inside: avoid` |
| Headings | `page-break-after: avoid` (heading + first paragraph stay together) |

Within a section, the rendering engine uses standard widow/orphan handling.

## Cover and end-page sizing in print

The cover and the end page must each render on **exactly one physical page**. Two failure modes have been observed and explicitly defended against:

### Failure mode — `min-height: 100vh` overflow

On screen, `.cover { min-height: 100vh; }` makes the cover fill the viewport. In print, `100vh` resolves to the **full paper height** (e.g. 1056 px on Letter), not the live content area after margins (~883 px on Letter at 0.8" outside / 1" bottom). The cover then overflows into a second physical page — and the second page picks up the body footer because `@page :first` only suppresses page 1, not the cover-overflow page.

### Failure mode — grid-row collapse in print

The cover uses `display: grid; grid-template-rows: auto 1fr auto;` on screen so the wordmark sits at the top, the title block centres vertically, and the metadata strip pins to the bottom. In print with `min-height: auto`, the `1fr` middle row collapses to zero, but `align-self: center` on `.cover-body` still positions its content visually. Edge then sees the grid section as shorter than the rendered content and inserts a page break at the (wrong) grid boundary — splitting the cover even with `break-inside: avoid` set, because the engine doesn't know the visual height exceeds the grid track.

The cover must therefore drop grid layout in print and use block flow.

### Required print overrides

Every implementation of the cover and end page must include these print-mode overrides:

```css
@media print {
  .cover {
    min-height: auto;             /* not 100vh */
    height: auto;
    display: block;               /* not grid — see grid-row collapse */
    grid-template-rows: none;
    padding: var(--s-6) 0 var(--s-5);
    border-bottom: none;
    page-break-after: always;
    break-after: page;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .cover-body  {
    align-self: auto;             /* reset grid centring */
    padding: var(--s-5) 0 var(--s-4);
  }
  .cover-title { font-size: 28pt; max-width: none; }
  .cover-subtitle { font-size: 13pt; }
  .end-page {
    min-height: auto;
    height: auto;
    display: block;               /* same reason */
    grid-template-rows: none;
    align-content: initial;
    justify-items: initial;
    padding: var(--s-7) 0 var(--s-6);
    border-top: none;
    page-break-before: always;
    break-before: page;
    page-break-inside: avoid;
    break-inside: avoid;
  }
}
```

The bundled `skill/assets/templates/document.html` ships these rules. Any custom document that re-derives the cover composition must include them.

### Verification

After producing a document, print-preview it in Chrome / Edge / Firefox / Safari. The cover must occupy exactly **one** page. The footer must be empty on page 1 (the cover). Body content must start on page 2 with footer "2". The end page must occupy the final page with no footer.

If the cover splits across two pages, the `min-height: 100vh` rule is winning. Verify the print overrides above are present and have not been overridden by a higher-specificity rule.

## Print background

Body background is `#FFFFFF` regardless of screen background. The stone-50 screen background is a screen-only convenience and does not appear in print. Stone tints in print appear only inside:

- Callouts.
- Code blocks.
- Banded table rows.
- Inline code chips.
- Cover eyebrow chip.

No stone-tinted page backgrounds in print.

## Print body size

Body type drops from 17 px (screen) to 10.5 pt (print). The reduction is empirical, not arithmetic — 10.5 pt produces 70-character lines on Letter at 0.8" margins, which is the editorial target.

Print scale:

| Element | Print size |
|---|---|
| H1 | 24 pt |
| H2 | 16 pt |
| H3 | 13 pt |
| H4 | 11 pt |
| Body | 10.5 pt |
| Lead | 12 pt |
| Small | 9.5 pt |
| Tiny / footer / labels | 8.5 pt |

## Body measure in print

`p, .lead, pre.code-block, .callout, .pullquote, table, ul, ol { max-width: 100%; }`

The 70-character screen `--measure` is removed in print because page margins already provide the constraint. The body fills the full live content area.

## Link rendering in print

`a { color: var(--deccan-blue); text-decoration: underline; }`

Underline is preserved; hover and focus styles are not relevant in print.

## What not to do

- Do not introduce per-document `@page` overrides.
- Do not change the footer copy.
- Do not switch to "Page X of Y" — the bare integer is the convention.
- Do not introduce a header. The system has no running header.
- Do not put stone-50 (or any tint) on the page background in print.
- Do not change margins on a per-document basis. 0.8" / 1" is the standard.
- Do not introduce coloured page edges or banner bands.
- Do not embed Deccan Green in a non-sustainability print context.

## Browser print quirks (informational)

- **Chrome / Edge:** "Print backgrounds" must be on for stone-100 callouts and code blocks to render. Set in the print dialog's More settings.
- **Firefox:** Same option, named "Print backgrounds".
- **Safari:** "Print backgrounds" lives in the print dialog under Show Details → Safari.

If the user reports "code blocks look white in the PDF", the print-backgrounds option is the cause.

## PDF generation policy

PDFs are produced on demand by the user. Do not invoke `Word.Application`, `PowerPoint.Application`, or `Excel.Application` COM automation to render PDFs — those calls hang on Trust Center / licence dialogs on the corporate fleet.

The two supported routes:

1. **From Word / PowerPoint / Excel** — `File → Export → Create PDF/XPS Document`. Embeds the OS-resident font; produces a faithful PDF.
2. **From HTML** — `wkhtmltopdf` against the HTML deliverable on a machine that has the resident fonts available, or print-to-PDF from a modern browser with "Print backgrounds" enabled.

Sandbox-rendered PDFs are not committed to the repository.
