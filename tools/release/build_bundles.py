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

`--sync-versions` / `--check` also keep the version literals outside skill/
(the MSI / PKG definitions and the README's stated package release) equal to
the skill frontmatter version, so installers can no longer ship stating a
package version two releases old.

Usage:
    python tools/release/build_bundles.py --out dist/
    python tools/release/build_bundles.py --check --out dist/   # verify only
    python tools/release/build_bundles.py --sync-plugin         # refresh mirror
    python tools/release/build_bundles.py --sync-versions       # sync version literals
"""

from __future__ import annotations

import argparse
import json
import re
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

# Files outside skill/ that state the package version. These drifted for
# two releases (installers shipped saying 2.1.2 while the package was at
# 2.3.x) because nothing gated them. Each entry: repo-relative path, a
# lookaround regex whose whole match is the version literal, and the exact
# number of matches the file must contain — a changed count means the file
# was restructured and this table needs updating, which should fail loudly.
VERSIONED_FILES = [
    ("installers/windows/deccan-design.wxs",
     r'(?<=Version=")\d+\.\d+\.\d+(?=")', 1),
    ("installers/windows/deccan-design.wxs",
     r'(?<=Name="Version" Value=")\d+\.\d+\.\d+(?=")', 1),
    ("installers/macos/deccan-design.pkgproj",
     r'(?<=<VERSION>)\d+\.\d+\.\d+(?=</VERSION>)', 2),
    ("installers/macos/build.sh",
     r'(?<=^VERSION=")\d+\.\d+\.\d+(?=")', 1),
    ("README.md",
     r'(?<=current package release \*\*v)\d+\.\d+\.\d+(?=\*\*)', 1),
    ("README.md",
     r'(?<=\(package v)\d+\.\d+\.\d+(?=\))', 1),
]


def check_versions() -> list[str]:
    """Every version literal outside skill/ must equal the skill version."""
    version = skill_version()
    problems = []
    for rel, pattern, expected in VERSIONED_FILES:
        text = (REPO / rel).read_text("utf-8")
        found = re.findall(pattern, text, flags=re.MULTILINE)
        if len(found) != expected:
            problems.append(
                f"{rel}: expected {expected} version literal(s) matching "
                f"{pattern!r}, found {len(found)}"
            )
        problems.extend(
            f"{rel}: states version {value}, package is {version}"
            for value in found if value != version
        )
    return problems


def sync_versions() -> None:
    """Rewrite every tracked version literal to the skill version."""
    version = skill_version()
    for rel, pattern, expected in VERSIONED_FILES:
        path = REPO / rel
        new, count = re.subn(pattern, version, path.read_text("utf-8"), flags=re.MULTILINE)
        if count != expected:
            raise SystemExit(
                f"{rel}: expected {expected} version literal(s) matching "
                f"{pattern!r}, matched {count} — update VERSIONED_FILES"
            )
        path.write_text(new, "utf-8")
    print(f"  version literals synced to {version} in "
          f"{len({rel for rel, _, _ in VERSIONED_FILES})} files")


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


# Markers the template itself must carry. A document built from a template
# missing any of these renders dark-on-dark in the Claude iOS and Android
# previews, which is the defect this list exists to make unshippable.
TEMPLATE_CONTRACT = (
    '<meta name="color-scheme" content="light">',
    "color-scheme: light only;",
    ":root { background-color: var(--stone-50) !important; }",
    "@media (prefers-color-scheme: dark) {",
    "main.body { padding: var(--s-8) var(--side-pad) var(--s-6); }",
)


def policy_problems(skill: str, slots: str, template: str) -> list[str]:
    """Every policy the skill must ship, checked against file *contents*.

    Taking text rather than paths lets the same list run against the working
    tree and against the built zip. The two used to be separate marker lists —
    one here, one inlined in the release workflow — and renaming a section
    updated one of them, which is how a release comes to fail on a rule that
    was strengthened rather than dropped.
    """
    problems = []

    # Attribution: without a resolution order, sessions attribute documents to
    # whoever the repository is about rather than whoever asked.
    if "## Attribution" not in skill:
        problems.append("SKILL.md: '## Attribution' section missing")
    else:
        attribution = skill.split("## Attribution", 1)[1].split("\n## ", 1)[0]
        if "Repository provenance is not authorship" not in attribution:
            problems.append("SKILL.md: Attribution section lost the provenance ban")
        if "ask the user" not in attribution:
            problems.append("SKILL.md: Attribution section lost the ask-the-user fallback")
        if "never a fallback" not in attribution:
            problems.append("SKILL.md: Attribution section lost the no-team-default rule")
    if "never the repo maintainer, never invented" not in skill:
        problems.append("SKILL.md: attribution checklist line missing")
    if "## PREPARED_BY resolution" not in slots:
        problems.append("document-slots.md: '## PREPARED_BY resolution' section missing")

    # Research reports: HTML default, Word on request, hyperlinked TOC,
    # light-only unless the user asks otherwise.
    if "## Research reports" not in skill:
        problems.append("SKILL.md: '## Research reports' section missing")
    else:
        research = skill.split("## Research reports", 1)[1].split("\n## ", 1)[0]
        for marker, label in ((            "HTML is the default", "the HTML-by-default rule"),
                              ("TOC \\o \"1-3\" \\h", "the hyperlinked Word TOC field"),
                              ("Light-only is the hard default", "the light-only default")):
            if marker not in research:
                problems.append(f"SKILL.md: Research reports section lost {label}")
    if ".toc li a" not in template:
        problems.append("document.html: the linked-TOC styling (.toc li a) is missing")

    # The skill is the org default for any stylized artifact, not only
    # Deccan-named requests.
    if "whether or not Deccan is mentioned" not in skill.split("---", 2)[1]:
        problems.append("SKILL.md: description no longer covers non-Deccan-named requests")

    # Fetch-first, and the ban on inheriting a prior document's stylesheet.
    # Together these are what stop an installed bundle — which always lags
    # eventually — from producing documents built on a frozen template.
    if "## Fetching the template — hard rule" not in skill:
        problems.append("SKILL.md: '## Fetching the template — hard rule' section missing")
    if "Fetch it at build time, every time" not in skill:
        problems.append("SKILL.md: the fetch-first directive is missing")
    if "Never fall back silently." not in skill:
        problems.append("SKILL.md: the fallback must be declared, not silent")
    if "## Revising an existing document" not in skill:
        problems.append("SKILL.md: '## Revising an existing document' section missing")

    # Cache defeat: a plain fetch of the unchanged canonical URL is routinely
    # answered by a cache (CDN, fetch tool, the conversation's own earlier
    # fetch) with a body that predates the current release — the rule above is
    # satisfied while the bytes are stale. Three markers close the gaps:
    # unique-query fetches, one fetch per document build, and the bundled
    # revision as a freshness floor on what a fetch may return.
    if "unique query string" not in skill:
        problems.append("SKILL.md: the cache-busting unique-query directive is missing")
    if "One fetch per document build" not in skill:
        problems.append("SKILL.md: the per-build fetch rule is missing")
    if "Freshness floor" not in skill:
        problems.append("SKILL.md: the freshness-floor rule is missing")
    if "unique query string" not in template:
        problems.append("document.html: the cache-busting fetch note is missing from the header")

    # The invariant is the backstop: a property of the artifact, checkable
    # without knowing what the session believed about its inputs.
    if "## The rendering invariant" not in skill:
        problems.append("SKILL.md: '## The rendering invariant' section missing")
    else:
        invariant = skill.split("## The rendering invariant", 1)[1].split("\n## ", 1)[0]
        for marker in ("color-scheme: light only;",
                       ":root { background-color: var(--stone-50) !important; }",
                       "@media (prefers-color-scheme: dark) {"):
            if marker not in invariant:
                problems.append(f"SKILL.md: the invariant does not list {marker!r}")
    if 'name="generator"' not in skill:
        problems.append("SKILL.md: the generator-meta self-check is missing")

    # And the template must actually satisfy the contract the skill advertises.
    for marker in TEMPLATE_CONTRACT:
        if marker not in template:
            problems.append(f"document.html: contract marker missing: {marker!r}")

    return problems


def _tree_text() -> tuple[str, str, str]:
    root = REPO / "skill"
    return (
        (root / "SKILL.md").read_text("utf-8"),
        (root / "assets" / "templates" / "document-slots.md").read_text("utf-8"),
        (root / "assets" / "templates" / "document.html").read_text("utf-8"),
    )


def verify_attribution() -> None:
    """Run the policy checks against the working tree."""
    problems = policy_problems(*_tree_text())
    if problems:
        raise SystemExit(
            "Skill policy incomplete:\n  " + "\n  ".join(problems)
        )


def verify_bundle(zip_path: Path) -> None:
    """Run the same policy checks against a built bundle.

    Defense in depth for the release job: the tree can be correct while the
    zip is built from a stale checkout, and Claude.ai rejects a bundle whose
    SKILL.md is not at the root of the single top-level folder.
    """
    with zipfile.ZipFile(zip_path) as z:
        names = sorted(i.filename for i in z.infolist())
        if "deccan-design/SKILL.md" not in names:
            raise SystemExit("bundle: SKILL.md must sit at the root of deccan-design/")
        texts = tuple(
            z.read(f"deccan-design/{rel}").decode("utf-8")
            for rel in ("SKILL.md",
                        "assets/templates/document-slots.md",
                        "assets/templates/document.html")
        )
    problems = policy_problems(*texts)
    if problems:
        raise SystemExit(
            f"{zip_path.name} does not carry the shipped policy:\n  " + "\n  ".join(problems)
        )
    print(f"{zip_path.name}: {len(names)} files; policy and template contract intact")


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
    problems = check_plugin() + check_versions()
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
    parser.add_argument(
        "--sync-versions", action="store_true",
        help="rewrite installer/README version literals to the skill version and exit",
    )
    parser.add_argument(
        "--verify-bundle", metavar="ZIP",
        help="run the policy checks against a built bundle and exit",
    )
    args = parser.parse_args()
    if args.sync_plugin:
        sync_plugin()
        return
    if args.sync_versions:
        sync_versions()
        return
    if args.verify_bundle:
        verify_bundle(Path(args.verify_bundle))
        return
    out_dir = Path(args.out)
    if args.check:
        check(out_dir)
    else:
        build(out_dir)


if __name__ == "__main__":
    main()
