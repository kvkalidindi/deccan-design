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

This tool also owns the Claude Code plugin mirror at plugin/skills/deccan-design/
(the repo doubles as a plugin marketplace; plugins discover skills only under
their own skills/ directory, so the skill tree is mirrored there byte-for-byte).
`--sync-plugin` refreshes the mirror and plugin.json's version from the skill
frontmatter; `--check` fails when the mirror or the version has drifted.

Usage:
    python tools/release/build_bundles.py --out dist/
    python tools/release/build_bundles.py --check --out dist/   # verify only
    python tools/release/build_bundles.py --sync-plugin         # refresh mirror
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SKILL_BUNDLE = "deccan-design-skill-bundle.zip"
TEMPLATES_BUNDLE = "templates-bundle.zip"
PLUGIN_SKILL_ROOT = REPO / "plugin" / "skills" / "deccan-design"
PLUGIN_MANIFEST = REPO / "plugin" / ".claude-plugin" / "plugin.json"

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


def verify_frontmatter() -> None:
    """The frontmatter must pass Claude.ai's skill-upload validation.

    The uploader rejects bundles whose SKILL.md `description` exceeds 1024
    characters (observed in the admin UI, v2.1.0 bundle refused). Catch it
    here, where the release is built, instead of at the workspace upload —
    the one manual step in the pipeline is the worst place to discover it.
    """
    text = (REPO / "skill" / "SKILL.md").read_text("utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("SKILL.md: frontmatter block missing")
    front = text.split("---", 2)[1]
    fields = {}
    for line in front.splitlines():
        if line.startswith(("name:", "description:", "version:")):
            key, _, value = line.partition(":")
            fields[key] = value.strip()
    problems = []
    for required in ("name", "description", "version"):
        if not fields.get(required):
            problems.append(f"frontmatter field missing: {required}")
    description = fields.get("description", "")
    if len(description) > 1024:
        problems.append(
            f"description is {len(description)} characters; Claude.ai's "
            "skill upload rejects anything over 1024"
        )
    if problems:
        raise SystemExit("SKILL.md frontmatter invalid:\n  " + "\n  ".join(problems))


def verify_attribution() -> None:
    """The skill must ship its attribution and default-application policy.

    Documents were being attributed to the design-system maintainer because
    nothing told a session how to resolve the author; the policy in SKILL.md
    is the fix, and a release that drops it silently reintroduces the bug.
    Same for the broadened trigger: the skill is the org default for any
    stylized artifact, not only Deccan-named ones.
    """
    skill = (REPO / "skill" / "SKILL.md").read_text("utf-8")
    slots = (REPO / "skill" / "assets" / "templates" / "document-slots.md").read_text("utf-8")
    problems = []
    if "## Attribution" not in skill:
        problems.append("SKILL.md: '## Attribution' section missing")
    else:
        attribution = skill.split("## Attribution", 1)[1].split("\n## ", 1)[0]
        if "kvkalidindi" not in attribution:
            problems.append("SKILL.md: Attribution section lost the repo-slug ban")
    if "never the repo maintainer, never invented" not in skill:
        problems.append("SKILL.md: attribution checklist line missing")
    if "whether or not Deccan is mentioned" not in skill.split("---", 2)[1]:
        problems.append("SKILL.md: description no longer covers non-Deccan-named requests")
    if "## PREPARED_BY resolution" not in slots:
        problems.append("document-slots.md: '## PREPARED_BY resolution' section missing")
    if problems:
        raise SystemExit(
            "Attribution/default-application policy incomplete:\n  " + "\n  ".join(problems)
        )


def _plugin_expected() -> dict[Path, bytes]:
    """Plugin-mirror path -> the bytes its skill/ source currently holds."""
    return {
        PLUGIN_SKILL_ROOT / rel: (REPO / "skill" / rel).read_bytes()
        for rel in SKILL_FILES
    }


def sync_plugin() -> None:
    """Refresh the plugin mirror and pin plugin.json to the skill version."""
    version = skill_version()
    for dst, data in _plugin_expected().items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    manifest = json.loads(PLUGIN_MANIFEST.read_text("utf-8"))
    manifest["version"] = version
    PLUGIN_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"  plugin mirror synced ({len(SKILL_FILES)} files, plugin.json -> {version})")


def check_plugin() -> list[str]:
    problems = []
    for dst, data in _plugin_expected().items():
        rel = dst.relative_to(REPO)
        if not dst.is_file():
            problems.append(f"plugin mirror missing: {rel}")
        elif dst.read_bytes() != data:
            problems.append(f"plugin mirror stale: {rel} differs from skill/ source")
    try:
        manifest = json.loads(PLUGIN_MANIFEST.read_text("utf-8"))
    except (OSError, ValueError):
        problems.append(f"unreadable: {PLUGIN_MANIFEST.relative_to(REPO)}")
    else:
        if manifest.get("version") != skill_version():
            problems.append(
                f"plugin.json version {manifest.get('version')!r} != "
                f"skill frontmatter {skill_version()!r}"
            )
    return problems


def bundles() -> dict[str, dict[str, bytes]]:
    verify_frontmatter()
    verify_revision()
    verify_attribution()
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
    problems = check_plugin()
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
    parser.add_argument(
        "--sync-plugin", action="store_true",
        help="refresh plugin/skills/deccan-design/ from skill/ and exit",
    )
    args = parser.parse_args()
    if args.sync_plugin:
        sync_plugin()
        return
    out_dir = Path(args.out)
    if args.check:
        check(out_dir)
    else:
        build(out_dir)


if __name__ == "__main__":
    main()
