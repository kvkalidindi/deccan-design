# Typography

## Type stack

### Sans (primary)

```css
font-family:
  'Segoe UI Variable Display',
  'Segoe UI Variable Text',
  'Segoe UI Variable',
  'Segoe UI',
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  sans-serif;
```

- **Windows 11:** Segoe UI Variable (variable font, optical sizing).
- **Windows 10:** Segoe UI (static, metric-compatible).
- **macOS:** San Francisco via `system-ui`.
- **Terminal fallback:** generic `sans-serif`.

### Mono

```css
font-family:
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

- **Windows 11:** Cascadia Mono (ships with Windows Terminal).
- **Windows 7/8/10:** Consolas.
- **macOS:** SF Mono.
- **Terminal fallback:** generic `monospace`.

## Banned faces

Sans: Helvetica, Helvetica Neue, Univers, Arial, Calibri, Verdana, Times, Times New Roman, Garamond, Georgia.

Mono: Courier, Courier New, Lucida Console.

The chain terminates in generic fallbacks; a generic fallback is preferred over a worse-than-default named family.

## Scale — 1.25 minor third

| Token | Pixels (screen) | Points (print) | Use |
|---|---|---|---|
| `--fs-tiny` | 11 | 8.5 | Mono caps labels, folio numbers |
| `--fs-small` | 14 | 9.5 | Captions, footnotes, table cells |
| `--fs-body` | 17 | 10.5 | Body copy, list items, callout body |
| `--fs-lead` | 21 | 13 | Lead paragraph at section opening |
| `--fs-h4` | 19 | 11 | H4 |
| `--fs-h3` | 24 | 13 | H3 |
| `--fs-h2` | 32 | 16 | H2 |
| `--fs-h1` | 44 | 24 | H1 |
| `--fs-display` | 64 | — | Cover, end page display |

## Weight ladder (size–weight inversion)

| Element | Weight |
|---|---|
| Display, H1 | 350 |
| H2 | 500 |
| H3, H4, `<strong>` | 600 |
| Body, lead, `<em>` | 400 |
| Mono labels | 600 |

As size grows, weight drops; large type does not overwhelm the page.

## Line height

| Token | Value | Use |
|---|---|---|
| `--lh-tight` | 1.15 | H1, display |
| `--lh-snug` | 1.30 | H2, H3, table headers |
| `--lh-base` | 1.65 | Body copy, list items, callouts |
| `--lh-loose` | 1.85 | Pull quotes, generous editorial leads |

## Measure

- **Screen:** 70 characters (`max-width: 70ch`) for body prose, callouts, code blocks, tables, lists, pull quotes.
- **Print:** full live content area. The print body is 10.5 pt on Letter at 0.8" outside margins, which produces 70-character lines without the screen `--measure` cap.

## Letter spacing

| Element | Letter-spacing |
|---|---|
| Display, H1 | `-0.024em` (display), `-0.022em` (H1) |
| H2 | `-0.012em` |
| H3, pull quote, strong | `-0.005em` |
| Mono caps labels | `+0.06em` to `+0.1em` |

## Optical sizing

Body has `font-optical-sizing: auto` set globally. Segoe UI Variable on Windows and SF Pro on macOS use their optical-sizing axes — letterforms thicken slightly at small sizes and thin slightly at large sizes. Cumulative across a document, this produces the rhythm that distinguishes editorial from corporate-deck typography.
