# Colour tokens

Complete reference for the deccan-design v2.0 palette.

## Deccan Blue — primary accent

| Token | Hex | RGB | RGBA | HSL |
|---|---|---|---|---|
| `--deccan-blue` | `#164999` | `22, 73, 153` | `rgba(22, 73, 153, 1.00)` | `217°, 75%, 34%` |
| `--deccan-blue-90` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.90)` | — |
| `--deccan-blue-60` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.60)` | — |
| `--deccan-blue-30` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.30)` | — |
| `--deccan-blue-15` | — | `22, 73, 153` | `rgba(22, 73, 153, 0.15)` | — |

Used for: headings on cover/end page, mark rule, callout left rule, link colour, table-header underline, focus ring base, section accent rules.

## Deccan Green — confined use only

| Token | Hex | RGB | HSL |
|---|---|---|---|
| `--deccan-green` | `#71BF4D` | `113, 191, 77` | `100°, 49%, 53%` |

Appears only in:

1. The Deccan wordmark where the full-colour mark is reproduced.
2. Sustainability content — BRSR / ESG / regulatory submissions, plant emissions narratives, QHSE policy.

Never a UI accent. Never a button colour. Documents that introduce `#71BF4D` outside the two contexts above fail review.

## Stone — neutral grayscale (ten stops)

| Token | Hex | RGB | HSL |
|---|---|---|---|
| `--stone-50` | `#FAFAF9` | `250, 250, 249` | `60°, 9%, 98%` |
| `--stone-100` | `#F5F5F4` | `245, 245, 244` | `60°, 5%, 96%` |
| `--stone-200` | `#E7E5E4` | `231, 229, 228` | `20°, 6%, 90%` |
| `--stone-300` | `#D6D3D1` | `214, 211, 209` | `24°, 6%, 83%` |
| `--stone-400` | `#A8A29E` | `168, 162, 158` | `24°, 5%, 64%` |
| `--stone-500` | `#78716C` | `120, 113, 108` | `25°, 5%, 45%` |
| `--stone-600` | `#57534E` | `87, 83, 78` | `33°, 5%, 32%` |
| `--stone-700` | `#44403C` | `68, 64, 60` | `30°, 6%, 25%` |
| `--stone-800` | `#292524` | `41, 37, 36` | `12°, 6%, 15%` |
| `--stone-900` | `#1C1917` | `28, 25, 23` | `24°, 10%, 10%` |

## Paper

`--paper: #FFFFFF`. Cover background, end-page background, table-cell background, print page background. Not aliased to a stone.

## CSS token block (copy-paste)

See `skill/references/tokens.md` for the canonical `:root` block.
