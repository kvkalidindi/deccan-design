"""Export the bundled design kit onto the local machine.

The converter binary carries the complete deccan-design v2.0 kit under
assets_data/kit/: every Office and Google Workspace template, the Outlook
and Gmail signatures, and the Claude skill (rules, tokens, slot template,
logo). `deccan-convert --export-kit DIR` writes it out so an offline
endpoint — no repo checkout, no network — has the full design system from
the single downloaded binary.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from deccan_convert import __version__
from deccan_convert.assets import assets_dir

KIT_DIR_NAME = "deccan-design-kit"

_KIT_README = f"""\
# deccan-design kit (exported by deccan-convert {__version__})

The complete deccan-design v2.0 design system, written out from the
converter's bundled assets. Everything here works offline; nothing is
fetched from the network.

| Directory | Contents |
|---|---|
| `templates/word/` | Word templates (.dotx): document, technical spec, policy, customer letter |
| `templates/excel/` | Excel templates (.xltx): workbook, comparison, financial model |
| `templates/powerpoint/` | PowerPoint templates (.potx): deck, customer pitch, internal review |
| `templates/outlook/` | Outlook signature (HTML + plain text, {{{{NAME}}}}/{{{{ROLE}}}}/{{{{EMAIL}}}}/{{{{PHONE}}}} placeholders) |
| `templates/gworkspace/` | Google Workspace files (upload to Drive, then File > Save as Google Docs/Sheets/Slides) + Gmail signature |
| `skill/` | The Anthropic Claude skill: design rules, tokens, print contract, slot template, logo assets |

## Installing the Office templates (per user, no admin rights)

- **Windows:** copy `templates/word|excel|powerpoint/*` into
  `%APPDATA%\\Microsoft\\Templates`, then in Word/Excel/PowerPoint use
  File > New > Personal.
- **macOS:** copy them into
  `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates`.

## Email signatures

- **Outlook:** fill the four placeholders in `templates/outlook/deccan-signature.htm`
  (the repository's Set-DeccanSignature helpers automate this) and register it
  under Settings > Accounts > Signatures.
- **Gmail:** open `templates/gworkspace/deccan-gmail-signature.html` in a browser,
  fill the placeholders, select all, and paste into
  Gmail Settings > General > Signature.

## Equipping a Claude environment (offline)

Copy the `skill/` directory into a repository as
`.claude/skills/deccan-design/` — Claude Code loads repo-level skills
automatically, so any session with that checkout applies the design system
with no network access and no endpoint install:

    cp -r skill/ <your-repo>/.claude/skills/deccan-design/

When the logo asset cannot be used, the text wordmark ("Deccan Fine
Chemicals" with the blue rule) is the sanctioned rendering — do not fetch
a logo from anywhere.

deccan-design v2.0 · Deccan Fine Chemicals Pvt. Ltd.
"""


def export_kit(dest: Path) -> Path:
    """Write the bundled kit to dest/deccan-design-kit; returns that path."""
    kit_src = assets_dir() / "kit"
    if not kit_src.is_dir():
        raise FileNotFoundError(
            "Bundled kit not found. In a dev checkout run: "
            "python tools/converter/sync_assets.py"
        )
    target = Path(dest) / KIT_DIR_NAME
    if target.exists():
        raise FileExistsError(
            f"{target} already exists - remove it or choose another directory."
        )
    shutil.copytree(kit_src, target)
    (target / "README.md").write_text(_KIT_README, encoding="utf-8")
    return target
