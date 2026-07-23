# Components

Every Deccan document is assembled from this component set. Each component has one reason to exist and one rule about when to use it.

## Cover page

Three regions, top to bottom:

1. **Wordmark.** 56-pixel-wide × 3-pixel Deccan Blue rule paired with the company name in semibold at 18 px, stone-900.
2. **Centred title block.** Eyebrow chip on stone-100 in mono caps at `--fs-tiny`. Title in Deccan Blue, weight 350, `--fs-display` (or `clamp(40px, 6.4vw, --fs-display)`), max width 22 ch, letter-spacing `-0.024em`. Subtitle below at 22 px, weight 400, stone-700, max 50 ch.
3. **Metadata strip.** Five-column grid across the bottom: Document type · Prepared by · Date · Version · Classification. Labels in mono uppercase at 10 px stone-500; values in semibold at `--fs-small` stone-900. Top border 1px stone-200.

Mandatory. No header, no footer, no page number. The first body section starts on the next page.

```html
<section class="cover">
  <div class="mark">
    <div class="mark-rule"></div>
    <div class="mark-text">Deccan Fine Chemicals</div>
  </div>
  <div class="cover-body">
    <span class="cover-eyebrow">{{DOCUMENT_TYPE}}</span>
    <h1 class="cover-title">{{TITLE}}</h1>
    <p class="cover-subtitle">{{SUBTITLE}}</p>
  </div>
  <dl class="cover-meta">
    <div><dt>Document type</dt><dd>{{DOCUMENT_TYPE}}</dd></div>
    <div><dt>Prepared by</dt><dd>{{PREPARED_BY}}</dd></div>
    <div><dt>Date</dt><dd>{{DATE}}</dd></div>
    <div><dt>Version</dt><dd>{{VERSION}}</dd></div>
    <div><dt>Classification</dt><dd>{{CLASSIFICATION}}</dd></div>
  </dl>
</section>
```

## End page

Self-contained. Centred wordmark, centred Deccan Blue rule (56px × 3px), centred contact line in `--fs-small` stone-600, classification reminder in mono caps stone-500. No header, no footer, no page number.

```html
<section class="end-page">
  <div class="end-mark">Deccan Fine Chemicals</div>
  <div class="end-rule"></div>
  <div class="end-contact">deccanchemicals.com · Hyderabad, India</div>
  <div class="end-classification">Confidential · Internal use</div>
</section>
```

## Heading hierarchy

Four levels. Each level has a defined typographic identity.

- **H1** — `--fs-h1` / 44 px screen / 24 pt print, weight 350, letter-spacing `-0.022em`, line-height `--lh-tight`, stone-900. 2-pixel solid stone-900 bottom rule. `page-break-before: always`. Optional eyebrow `.num` carries a section number in decimal-leading-zero mono.
- **H2** — `--fs-h2` / 32 px / 16 pt, weight 500, letter-spacing `-0.012em`, line-height `--lh-snug`, stone-900.
- **H3** — `--fs-h3` / 24 px / 13 pt, weight 600, letter-spacing `-0.005em`, line-height 1.2, stone-900.
- **H4** — `--fs-h4` / 19 px / 11 pt, weight 600, line-height 1.25, stone-900.

All headings carry `page-break-after: avoid`.

## Lead paragraph

`--fs-lead` / 21 px / 13 pt, weight 400, stone-700, line-height 1.5, max width 60 ch. Class `.lead`. Used to open a section with a thesis statement. Optional.

## Body

`--fs-body` / 17 px / 10.5 pt, weight 400, stone-800, line-height `--lh-base`. Body measure 70 ch on screen, full content width in print.

## Callout

Stone-100 fill, three-pixel Deccan Blue left rule, mono-caps label in stone-500, body in body type.

```html
<div class="callout">
  <div class="label">Provisioning rule</div>
  <p>Body text.</p>
</div>
```

Variant `.callout.muted`: left rule in stone-700 instead of Deccan Blue. Use for asides about the system itself, where Deccan Blue would over-emphasise.

## Code chip and code block

**Inline:** `<code>like this</code>` — mono, 0.92em, stone-100 fill, 1px × 6px padding, stone-900 ink.

**Block:** `<pre class="code-block">` — stone-100 fill, `--s-4 --s-5` padding, mono 13 px, line-height 1.55, stone-900 ink, `overflow-x: auto`, `page-break-inside: avoid`.

**Discipline rule:** mono and stone always travel together. Mono on a white background reads as a typo; stone-100 on sans body reads as a callout. Together they read as code.

## Pull quote

Indented with a 3-pixel Deccan Blue left rule, max 60 ch, 22 px stone-700, weight 400, line-height 1.4, letter-spacing `-0.005em`. No quote marks.

## Table

Headers: mono uppercase at 11 px, weight 600, letter-spacing `0.06em`, stone-700 ink, stone-100 fill, 2-pixel solid stone-900 bottom rule.

Body cells: body type, padding `--s-3 --s-4`, stone-800 ink, 1-pixel stone-200 row separator.

Banded: `tbody tr:nth-child(even) td { background: var(--stone-50); }`.

No column borders. Tables hold their measure on screen and expand to full content width in print.

## Lists

- Bulleted: default disc marker, `li::marker { color: var(--stone-500); }`.
- Numbered: decimal markers in the same tint.
- Definition: semibold term, stone-200-bordered description block.

Indent 28 px from text start. List item bottom margin `--s-2`. Max width `--measure` on screen, full width in print.

## Links

Deccan Blue text. Default underline: 1-pixel Deccan Blue at 30% opacity, offset 3 pixels below baseline. Hover: full Deccan Blue. Focus: 2-pixel Deccan Blue at 30% opacity outline, 2-pixel offset.

```css
a {
  color: var(--deccan-blue);
  text-decoration-line: underline;
  text-decoration-color: var(--deccan-blue-30);
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}
a:hover { text-decoration-color: var(--deccan-blue); }
a:focus-visible {
  outline: 2px solid var(--deccan-blue-30);
  outline-offset: 2px;
}
```

## TOC

Container: stone-200 1-pixel border, stone-50 padding `--s-5 --s-6`, max 720 px. Label in mono caps stone-700 with a stone-200 underline. Items in a numbered list with `decimal-leading-zero` counter in mono stone-500, 36-pixel counter column + content column.

## Sidenote (optional)

Aside placed in the margin on wide screens, inline on narrow. Body type at `--fs-small` stone-600. Optional component — not in every document.

## Logo / mark variants

- Full-colour wordmark (default).
- Monochrome black on white (constrained print).
- Monochrome white on Deccan Blue (cover variant, single-colour print).
- Sustainability-context mark: full-colour, with Deccan Green retained.

See `assets/logo.svg`, `assets/logo.png`, `assets/logo.b64.txt` for the asset cascade.

## What is not a component

- No badge / pill widgets.
- No card with shadow.
- No accent rule under titles in slides (the AI-slop tell).
- No accordion / disclosure widget — not a document idiom.
- No tab widget — not a document idiom.

Components added in future versions go through the design-system owner. Documents that introduce one-off components fail review.
