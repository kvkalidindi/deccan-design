# Tokens

Authoritative colour, type, scale, and spacing tokens for deccan-design v2.0.

## Colour

### Deccan Blue — primary accent

One accent. Hierarchy derived from opacity, not from a second hue.

| Token | Hex | RGB | RGBA | Use |
|---|---|---|---|---|
| `--deccan-blue` | `#164999` | `22, 73, 153` | `rgba(22, 73, 153, 1.00)` | Primary accent — headings on cover/end page, mark rule, callout left rule, link colour, table-header underline, focus ring base, section accent rules |
| `--deccan-blue-90` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.90)` | Hover state |
| `--deccan-blue-60` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.60)` | Secondary structural use |
| `--deccan-blue-30` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.30)` | Link underline default, focus-ring outline |
| `--deccan-blue-15` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.15)` | Subtle wash, chart-series fill |

### Deccan Green — confined use only

`--deccan-green: #71BF4D` — RGB `113, 191, 77`. Appears **only** in:

1. The official Deccan wordmark where the full-colour mark is reproduced.
2. Content explicitly about sustainability — environmental reporting, BRSR / ESG / regulatory submissions, plant emissions narratives, QHSE policy.

Not a UI accent. Not a button colour. Not a "secondary brand colour". Documents that introduce `#71BF4D` outside the two contexts above fail review.

### Stone — neutral grayscale

Ten stops. Use:

| Token | Hex | RGB | HSL | Use |
|---|---|---|---|---|
| `--stone-50` | `#FAFAF9` | `250, 250, 249` | `60° 9% 98%` | Page background (screen only); banded table row |
| `--stone-100` | `#F5F5F4` | `245, 245, 244` | `60° 5% 96%` | Code chip / block fill; callout fill; mono-caps eyebrow chip |
| `--stone-200` | `#E7E5E4` | `231, 229, 228` | `20° 6% 90%` | Hairline rules; cell borders; section dividers |
| `--stone-300` | `#D6D3D1` | `214, 211, 209` | `24° 6% 83%` | Disabled element; chart axis |
| `--stone-400` | `#A8A29E` | `168, 162, 158` | `24° 5% 64%` | Decorative — folio numbers, watermarks |
| `--stone-500` | `#78716C` | `120, 113, 108` | `25° 5% 45%` | Mono-caps labels; secondary captions; footer page number |
| `--stone-600` | `#57534E` | `87, 83, 78` | `33° 5% 32%` | Tertiary body text |
| `--stone-700` | `#44403C` | `68, 64, 60` | `30° 6% 25%` | Lead paragraph; subtitle; muted-callout rule |
| `--stone-800` | `#292524` | `41, 37, 36` | `12° 6% 15%` | Body copy default |
| `--stone-900` | `#1C1917` | `28, 25, 23` | `24° 10% 10%` | Headings; ink colour; `--ink` alias |

### Paper

`--paper: #FFFFFF`. Cover background, end-page background, table-cell background, print page background. Not aliased to a stone.

### Token CSS block (copy-paste)

```css
:root {
  --deccan-blue:     #164999;
  --deccan-blue-90:  rgba(22, 73, 153, 0.90);
  --deccan-blue-60:  rgba(22, 73, 153, 0.60);
  --deccan-blue-30:  rgba(22, 73, 153, 0.30);
  --deccan-blue-15:  rgba(22, 73, 153, 0.15);
  --deccan-green:    #71BF4D;
  --stone-50:        #FAFAF9;
  --stone-100:       #F5F5F4;
  --stone-200:       #E7E5E4;
  --stone-300:       #D6D3D1;
  --stone-400:       #A8A29E;
  --stone-500:       #78716C;
  --stone-600:       #57534E;
  --stone-700:       #44403C;
  --stone-800:       #292524;
  --stone-900:       #1C1917;
  --paper:           #FFFFFF;
  --ink:             var(--stone-900);
}
```

## Type

### Sans (primary)

```css
--font-sans:
  'Segoe UI Variable Display',
  'Segoe UI Variable Text',
  'Segoe UI Variable',
  'Segoe UI',
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  sans-serif;
```

On Windows 11 the chain resolves to Segoe UI Variable, a variable font with optical sizing. On Windows 10 it falls back to the static Segoe UI faces (metric-compatible). On macOS the chain resolves to San Francisco via `system-ui`. No font binaries ship with the system.

### Mono

```css
--font-mono:
  'Cascadia Mono',
  'Cascadia Code',
  Consolas,
  'SF Mono',
  Menlo,
  'DejaVu Sans Mono',
  'Liberation Mono',
  ui-monospace,
  monospace;
```

Cascadia Mono on Windows 11 (ships with Windows Terminal). Cascadia Code is the same face with programming ligatures; Mono is the document default to keep ligatures out of prose. Consolas is the Windows 7/8/10 fallback. SF Mono on macOS.

### Banned faces

Sans: Helvetica, Helvetica Neue, Univers, Arial, Calibri, Verdana, Times, Times New Roman, Garamond, Georgia.

Mono: Courier, Courier New, Lucida Console.

## Scale — 1.25 minor third

| Token | Pixels (screen) | Points (print) | Use |
|---|---|---|---|
| `--fs-tiny` | 11 | 8.5 | Mono caps labels, folio numbers, captions |
| `--fs-small` | 14 | 9.5 | Captions, footnotes, table cells, metadata |
| `--fs-body` | 17 | 10.5 | Body copy, list items, callout body |
| `--fs-lead` | 21 | 13 | Lead paragraph at section opening |
| `--fs-h4` | 19 | 11 | Inline subsection heading |
| `--fs-h3` | 24 | 13 | H3 |
| `--fs-h2` | 32 | 16 | H2 |
| `--fs-h1` | 44 | 24 | H1 |
| `--fs-display` | 64 | — | Cover and end-page display |

## Weight — size–weight inversion

Variable-font systems treat weight as a continuous axis. As size grows, weight drops, so that large type does not overwhelm the page.

| Element | Weight |
|---|---|
| Display, H1 | 350 |
| H2 | 500 |
| H3, H4, `<strong>` | 600 |
| Body, lead, `<em>` | 400 |
| Mono labels | 600 |

## Line height

| Token | Value | Use |
|---|---|---|
| `--lh-tight` | 1.15 | H1, display |
| `--lh-snug` | 1.30 | H2, H3, table headers |
| `--lh-base` | 1.65 | Body copy, list items, callouts |
| `--lh-loose` | 1.85 | Pull quotes, generous editorial leads |

## Spacing — 8 px base

| Token | Value | Notional use |
|---|---|---|
| `--s-1` | 4px | Inline padding inside chips |
| `--s-2` | 8px | List item bottom margin; small label margin |
| `--s-3` | 12px | Cell padding (vertical); subhead bottom margin |
| `--s-4` | 16px | Paragraph bottom margin; callout vertical padding |
| `--s-5` | 24px | Section-level vertical rhythm |
| `--s-6` | 32px | H3 top margin; eyebrow-to-title |
| `--s-7` | 48px | H2 top margin; pull-quote vertical air |
| `--s-8` | 64px | Top-of-page padding for body |
| `--s-9` | 96px | Cover top padding; end-page padding |
| `--s-10` | 128px | Reserved for future use |

## Layout

| Token | Value |
|---|---|
| `--measure` | `70ch` (screen) / full live area (print) |
| `--content-max` | `1180px` |
| `--gutter` | `24px` |
| `--side-pad` | `clamp(20px, 4vw, 64px)` |

## Print page

`@page` size Letter (also valid for A4 without alteration), 0.8" outside margins, 1" bottom margin. Footer runs only on body pages — suppressed on cover and end page.

The full `@page` rule block is in `print-rules.md`.
