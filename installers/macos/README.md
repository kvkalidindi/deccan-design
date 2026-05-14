# macOS installer

`deccan-design.pkgproj` and `build.sh` produce an **unsigned per-user `.pkg`** for deccan-design v2.0.

## What it installs

| Component | Path |
|---|---|
| Office templates | `~/Library/Group Containers/UBF8T346G9.Office/User Content.localized/Templates.localized/` |
| Outlook signature template (unconfigured) | `~/Library/Containers/com.microsoft.Outlook/Data/Library/Signatures/deccan-signature-template.htm` |
| Bash signature helper | `~/Library/Application Support/deccan-design/set-deccan-signature.sh` |
| Claude skill | `~/Library/Application Support/Anthropic/Claude/skills/deccan-design/` |
| Documentation | `~/Library/Application Support/deccan-design/docs/` |
| Logo assets | `~/Library/Application Support/deccan-design/assets/` |

## Build

```bash
./build.sh
```

Output: `deccan-design-2.0.0.pkg` (unsigned).

The script uses `pkgbuild` + `productbuild`. If you have Packages.app installed (http://s.sudre.free.fr/Software/Packages/), you can also open `deccan-design.pkgproj` in the GUI and Build → Build there.

## Unsigned-installer warning

On every user's first install, Gatekeeper blocks the `.pkg` with:

> "deccan-design-2.0.0.pkg cannot be opened because Apple cannot check it for malicious software."

This is expected — the installer is unsigned per Decision 5 in PRD §1.4. Instruct the user to:

1. Right-click the `.pkg` in Finder → **Open** → confirm in the dialog. **Or**
2. Open **System Settings → Privacy & Security**. Click **Open Anyway** next to the blocked-app notice. Enter your password.

For Jamf-managed endpoints, push the `.pkg` via policy — Jamf-deployed packages bypass Gatekeeper entirely.

## Uninstall

```bash
sudo pkgutil --forget com.deccanchemicals.deccan-design
# Then manually remove the installed files:
rm -rf "$HOME/Library/Application Support/deccan-design"
rm -rf "$HOME/Library/Application Support/Anthropic/Claude/skills/deccan-design"
rm "$HOME/Library/Group Containers/UBF8T346G9.Office/User Content.localized/Templates.localized/deccan-"*
rm "$HOME/Library/Containers/com.microsoft.Outlook/Data/Library/Signatures/deccan-"*
rm "$HOME/Library/Containers/com.microsoft.Outlook/Data/Library/Signatures/Deccan."*
```

The admin guide includes this procedure for help-desk reference.

## Why no signing step

PRD §1.4 Decision 5 makes signing out of scope. The cost: every first install triggers Gatekeeper. The trade: no Apple Developer ID enrollment, no per-build signing or notarization step. The admin guide's "Unsigned-installer support runbook" covers the user-facing friction.
