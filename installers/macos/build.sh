#!/bin/bash
# deccan-design v2.0 — macOS .pkg build
#
# Produces an unsigned per-user .pkg at ./deccan-design-2.0.0.pkg.
#
# Run on a macOS machine. Two routes are supported:
#   1. Packages.app (preferred). Open deccan-design.pkgproj, Build → Build.
#   2. pkgbuild + productbuild (fallback, no Packages.app needed).
#
# This script implements route 2. The .pkg is intentionally unsigned per
# Decision 5 in PRD §1.4.

set -e

cd "$(dirname "$0")"

VERSION="2.0.0"
PKG_OUT="deccan-design-${VERSION}.pkg"
ROOT="../.."
STAGE="build/stage"
SCRIPTS="build/scripts"

echo "Cleaning previous build artifacts ..."
rm -rf build "$PKG_OUT"
mkdir -p "$STAGE" "$SCRIPTS"

# Stage payload under a $HOME-relative tree
USER_BASE="$STAGE/Users/Shared"  # placeholder — the postinstall script handles per-user copy
mkdir -p "$STAGE/payload"

# Office templates
TPL_OUT="$STAGE/payload/Library/Group Containers/UBF8T346G9.Office/User Content.localized/Templates.localized"
mkdir -p "$TPL_OUT"
cp "$ROOT/templates/word/"*.dotx "$TPL_OUT/"
cp "$ROOT/templates/excel/"*.xltx "$TPL_OUT/"
cp "$ROOT/templates/powerpoint/"*.potx "$TPL_OUT/"

# Outlook signature template
SIG_OUT="$STAGE/payload/Library/Containers/com.microsoft.Outlook/Data/Library/Signatures"
mkdir -p "$SIG_OUT"
cp "$ROOT/templates/outlook/deccan-signature.htm" "$SIG_OUT/deccan-signature-template.htm"
cp "$ROOT/templates/outlook/deccan-signature.txt" "$SIG_OUT/deccan-signature-template.txt"

# Helper script + skill + docs
APP_SUPPORT="$STAGE/payload/Library/Application Support/deccan-design"
mkdir -p "$APP_SUPPORT/docs" "$APP_SUPPORT/assets"
cp set-deccan-signature.sh "$APP_SUPPORT/set-deccan-signature.sh"
chmod +x "$APP_SUPPORT/set-deccan-signature.sh"
cp "$ROOT/README.md" "$APP_SUPPORT/docs/README.md" 2>/dev/null || true
cp "$ROOT/claude/personal-preferences.md" "$APP_SUPPORT/docs/personal-preferences.md" 2>/dev/null || true
cp "$ROOT/skill/assets/logo.png" "$APP_SUPPORT/assets/logo.png"
cp "$ROOT/skill/assets/logo.svg" "$APP_SUPPORT/assets/logo.svg"

# Claude skill (recursive)
SKILL_OUT="$STAGE/payload/Library/Application Support/Anthropic/Claude/skills/deccan-design"
mkdir -p "$SKILL_OUT"
cp -R "$ROOT/skill/." "$SKILL_OUT/"

# Postinstall (relocate from /Library to ~/Library)
cp scripts/preinstall "$SCRIPTS/preinstall"
cp scripts/postinstall "$SCRIPTS/postinstall"

# Wrap relocation: the .pkg's INSTALL_DESTINATION is /, and a postinstall
# script copies the staged payload into the user's home. This pattern is
# necessary because pkgbuild does not support ~/ install destinations natively.
cat > "$SCRIPTS/postinstall" <<'POSTINSTALL'
#!/bin/bash
set -e
USER_HOME="$(eval echo ~$USER)"
SRC="/Library/Application Support/deccan-design.payload"

if [ -d "$SRC" ]; then
    rsync -a "$SRC/" "$USER_HOME/"
    rm -rf "$SRC"
fi

# Write the preferences reminder
REMINDER="$USER_HOME/Library/Application Support/deccan-design/preferences-reminder.txt"
cat > "$REMINDER" <<EOF
Action required: configure Claude.ai personal preferences.

Paste the text from claude/personal-preferences.md into
Claude.ai -> Settings -> Profile -> Preferences:
  https://claude.ai/settings

The local copy lives at:
  ~/Library/Application Support/deccan-design/docs/personal-preferences.md

Repository: https://github.com/kvkalidindi/deccan-design
EOF

chmod +x "$USER_HOME/Library/Application Support/deccan-design/set-deccan-signature.sh" 2>/dev/null || true

exit 0
POSTINSTALL
chmod +x "$SCRIPTS/postinstall" "$SCRIPTS/preinstall"

# Stage payload at /Library/Application Support/deccan-design.payload
RELOC_ROOT="$STAGE/Library/Application Support/deccan-design.payload"
mkdir -p "$RELOC_ROOT"
rsync -a "$STAGE/payload/" "$RELOC_ROOT/"
rm -rf "$STAGE/payload"

echo "Running pkgbuild ..."
pkgbuild \
    --root "$STAGE" \
    --identifier "com.deccanchemicals.deccan-design" \
    --version "$VERSION" \
    --scripts "$SCRIPTS" \
    --install-location "/" \
    "build/deccan-design-component.pkg"

echo "Running productbuild ..."
cat > build/Distribution.xml <<DIST
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
  <title>deccan-design v${VERSION}</title>
  <organization>com.deccanchemicals</organization>
  <pkg-ref id="com.deccanchemicals.deccan-design" version="${VERSION}">deccan-design-component.pkg</pkg-ref>
  <choices-outline>
    <line choice="default">
      <line choice="com.deccanchemicals.deccan-design"/>
    </line>
  </choices-outline>
  <choice id="default"/>
  <choice id="com.deccanchemicals.deccan-design" visible="false">
    <pkg-ref id="com.deccanchemicals.deccan-design"/>
  </choice>
</installer-gui-script>
DIST

productbuild \
    --distribution build/Distribution.xml \
    --package-path build \
    "$PKG_OUT"

echo ""
echo "Built: $(pwd)/$PKG_OUT"
echo ""
echo "The .pkg is UNSIGNED. On install the user will see Gatekeeper:"
echo "  'deccan-design-${VERSION}.pkg cannot be opened because Apple"
echo "   cannot check it for malicious software.'"
echo ""
echo "Instruct the user to: right-click the .pkg -> Open -> confirm in dialog."
echo "Or: System Settings -> Privacy & Security -> 'Open Anyway'."
echo ""
echo "For silent enterprise deployment via Jamf, the MDM bypass is preferred."
