#!/usr/bin/env python3
"""Build the two release bundles attached to a `v*` design-system release.

`deccan-design-skill-bundle.zip`
    The `skill/` tree, re-rooted under a single `deccan-design/` folder —
    the layout Claude.ai's Settings → Workspace → Skills upload expects
    (`SKILL.md` at the root of that folder). This is also the payload the
    MSI / PKG lay down at the endpoint for Claude Code and Claude Desktop.

`templates-bundle.zip`
    The `templates/` tree verbatim, for endpoints that want the Office /
    Outlook / Workspace templates without running an installer.

Both zips are byte-stable: entries are sorted and stamped with a fixed
date_time, so rebuilding an unchanged tree produces an identical file and
`--check` can compare a published bundle against the repository sources.

Usage:
    python tools/release/build_bundles.py --out dist/
    python tools/release/build_bundles.py --check --out dist/   # verify only
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SKILL_BUNDLE = "deccan-design-skill-bundle.zip"
TEMPLATES_BUNDLE = "templates-bundle.zip"

# The skill bundle's exact contents. Held as a literal rather than globbed
# so a stray file under skill/ (an editor backup, a scratch note) can never
# reach a workspace upload, and so a dropped file fails the build loudly.
SKILL_FILES = [
    "SKILL.md",
    "references/tokens.md",
    "references/components.md",
    "references/print-rules.md",
    "references/tone-and-voice.md",
    "references/document-templates.md",
    "assets/logo.svg",
    "assets/logo.png",
    "assets/logo.b64.txt",
    "assets/fonts/README.md",
    "assets/templates/document.html",
    "assets/templates/document-slots.md",
    "assets/templates/README.md",
]

TEMPLATE_FILES = [
    "word/deccan-document.dotx",
    "word/deccan-technical-spec.dotx",
    "word/deccan-policy.dotx",
    "word/deccan-customer-letter.dotx",
    "excel/deccan-workbook.xltx",
    "excel/deccan-comparison.xltx",
    "excel/deccan-financial-model.xltx",
    "powerpoint/deccan-deck.potx",
    "powerpoint/deccan-customer-pitch.potx",
    "powerpoint/deccan-internal-review.potx",
    "outlook/deccan-signature.htm",
    "outlook/deccan-signature.txt",
    "gworkspace/deccan-document-for-drive.docx",
    "gworkspace/deccan-workbook-for-drive.xlsx",
    "gworkspace/deccan-deck-for-drive.pptx",
    "gworkspace/deccan-gmail-signature.html",
    "gworkspace/README.md",
]

# Fixed stamp keeps rebuilds byte-identical.
_STAMP = (2020, 1, 1, 0, 0, 0)


def _entries(src_root: str, files: list[str], dst_root: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for rel in files:
        src = REPO / src_root / rel
        if not src.is_file():
            raise SystemExit(f"Bundle source missing: {src}")
        out[f"{dst_root}/{rel}"] = src.read_bytes()
    return out


def skill_version() -> str:
    """The `version:` from the skill frontmatter — the release's identity."""
    for line in (REPO / "skill" / "SKILL.md").read_text("utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("skill/SKILL.md has no version in its frontmatter")


def verify_revision() -> str:
    """The slot template must name the revision it ships as.

    Sessions fetch document.html straight from the raw URL, where the only
    thing that says which copy they got is the marker in the file. A marker
    left behind at the previous release is worse than none: it reads as
    current. Both the header comment and the generator meta must agree with
    the skill version, or the release does not build.
    """
    version = skill_version()
    template = (REPO / "skill" / "assets" / "templates" / "document.html").read_text("utf-8")
    required = [
        f"slot-fill document template · revision {version}",
        f'<meta name="generator" content="deccan-design v2.0 · slot template {version}">',
    ]
    missing = [marker for marker in required if marker not in template]
    if missing:
        raise SystemExit(
            "document.html does not identify itself as revision "
            f"{version}; missing:\n  " + "\n  ".join(missing)
        )
    return version


def bundles() -> dict[str, dict[str, bytes]]:
    verify_revision()
    return {
        SKILL_BUNDLE: _entries("skill", SKILL_FILES, "deccan-design"),
        TEMPLATES_BUNDLE: _entries("templates", TEMPLATE_FILES, "templates"),
    }


def _write(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=_STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, entries[name])


def build(out_dir: Path) -> None:
    print(f"  slot template identifies as revision {verify_revision()}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, entries in bundles().items():
        path = out_dir / name
        _write(path, entries)
        print(f"  built {name}  ({len(entries)} files, {path.stat().st_size:,} bytes)")


def check(out_dir: Path) -> None:
    problems = []
    for name, entries in bundles().items():
        path = out_dir / name
        if not path.is_file():
            problems.append(f"missing: {name}")
            continue
        with zipfile.ZipFile(path) as z:
            names = sorted(i.filename for i in z.infolist())
            if names != sorted(entries):
                problems.append(f"contents differ: {name}")
                continue
            for entry, data in entries.items():
                if z.read(entry) != data:
                    problems.append(f"stale: {name} :: {entry}")
    if problems:
        print("Bundles do not match the repository sources:")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)
    print("Bundles match the repository sources.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="dist", help="output directory (default: dist)")
    parser.add_argument("--check", action="store_true", help="verify, do not write")
    args = parser.parse_args()
    out_dir = Path(args.out)
    if args.check:
        check(out_dir)
    else:
        build(out_dir)


if __name__ == "__main__":
    main()
