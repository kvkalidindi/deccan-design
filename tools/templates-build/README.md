# templates-build

Build and compliance tooling for the template suite in `templates/`. Ensures every Word / Excel / PowerPoint / Outlook / Google Workspace template strictly carries the deccan-design v2.0 tokens — including the parts users never see until they type new content (the OOXML theme, the built-in style gallery, the workbook default font).

**Never hand-edit the binary templates.** Change `build_templates.py` (or the source template it patches) and rerun it. The Google Workspace trio and the two specialised PowerPoint templates are *derived* files; the script regenerates them from their sources.

| Script | Use |
|---|---|
| `build_templates.py` | Patch the 10 Office template sources in place; regenerate `deccan-customer-pitch.potx` and `deccan-internal-review.potx` from the patched deck; re-derive the three `templates/gworkspace/` Office files. `--check` exits 1 if any output would change. |
| `verify_templates.py` | Read-only compliance scan: banned typefaces, stale Office hexes, furniture rules (Word footer contract, Excel gridlines/panes/print footer, PPT master footer styling), converter marker contract, derivation freshness. Runs in CI. |
| `deccan_tokens.py` | The token values, banned-face list, and the stale-hex → token remap table. Mirrors `skill/references/tokens.md`. |

## What the build enforces

- **Theme** (all 13 OOXML files): fontScheme = Segoe UI Variable Display / Text; clrScheme = stone-900/paper/stone-700/stone-100, accent1 Deccan Blue with accents 2–5 as its 90/60/30/15 blends on paper, accent6 stone-500, links Deccan Blue. New content typed by users inherits these instead of stock Calibri/`4F81BD`.
- **Word**: body-page footer "Deccan Fine Chemicals · Confidential" + bare PAGE number (Cascadia Mono 8.5 pt stone-500, right tab); cover and end sections keep no footer; Heading 4 = 11 pt w600 stone-900; Headings 5–9 tokenised; the entire built-in gallery (including `stylesWithEffects.xml`) remapped to tokens — every foreign accent hue collapses to Deccan Blue (single-accent system); banned faces stripped from `fontTable.xml`; Courier → Cascadia Mono in the macro styles.
- **Excel**: workbook default font Segoe UI Variable Text (was Calibri); screen gridlines off; header row frozen; Letter page setup with the running footer in the print footer.
- **PowerPoint**: master bullet fonts and text defaults tokenised; master footer / slide-number / date placeholders restyled to Cascadia Mono 8.5 pt stone-500 with the confidential footer text; customer-pitch and internal-review are genuinely specialised decks generated from `deccan-deck.potx` (they were previously byte-identical copies).
- **docProps**: creator/company "Deccan Fine Chemicals", per-template titles, fixed dates (byte-stable outputs).

## Run order

```bash
python tools/templates-build/build_templates.py     # patch + derive
python tools/converter/sync_assets.py               # refresh the converter's bundled copies
python -m pytest tools/converter/tests -q           # converter contract must hold
python tools/templates-build/verify_templates.py    # compliance scan
```

The converter (`tools/converter/`) bundles `deccan-workbook.xltx`, `deccan-deck-for-drive.pptx`, and a base docx derived from `deccan-document.dotx` — its CI drift check fails until `sync_assets.py` is re-run after any template change.

## Documented deviations

- **Excel print-footer size is 9 pt**, not the 8.5 pt token: Excel footer `&N` size codes accept integers only.
- **"Cambria Math" survives** in Word's `settings.xml` equation configuration. It is the equation-layout font (the only widely available OpenType math face), not a text face; the verify scan exempts exactly the string "Cambria Math".
- **OOXML theme fonts hold a single face**, not a CSS-style fallback chain. Machines without Segoe UI Variable substitute silently (per the no-font-embedding policy).
- **Legacy indexed-color palette** in Excel `styles.xml` is a fixed 56-color lookup table mandated by the format; it is exempt from the stale-hex scan.
- The gallery remap collapses Word's "Accent 2–6" table/list style families to Deccan Blue — users lose the red/green/purple variants by design (single-accent system).
