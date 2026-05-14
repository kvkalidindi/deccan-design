# Windows installer

`deccan-design.wxs` defines an **unsigned per-user MSI** for the deccan-design v2.0 system.

## What it installs

| Component | Path |
|---|---|
| Office templates (Word / Excel / PowerPoint) | `%APPDATA%\Microsoft\Templates\` |
| Outlook signature template (unconfigured) | `%APPDATA%\Microsoft\Signatures\deccan-signature-template.htm` |
| PowerShell signature helper | `%APPDATA%\deccan-design\Set-DeccanSignature.ps1` |
| Claude skill | `%APPDATA%\Anthropic\Claude\skills\deccan-design\` |
| Preferences reminder | `%APPDATA%\deccan-design\preferences-reminder.txt` |
| Documentation (offline copies) | `%APPDATA%\deccan-design\docs\` |
| Logo assets | `%APPDATA%\deccan-design\assets\` |

## Registry edits

- `HKCU\Software\Microsoft\Office\16.0\Common\General\PersonalTemplates` → `%APPDATA%\Microsoft\Templates`
- `HKCU\Software\deccan-design\Version` → `2.0.0`
- `HKCU\Software\deccan-design\InstallPath` → installation root

## Build

```powershell
# Requires WiX Toolset v4: dotnet tool install --global wix
.\build.ps1
```

Output: `deccan-design-2.0.0.msi` (unsigned).

## Unsigned-installer warning

On every user's first install they will see **SmartScreen** ("Windows protected your PC"). This is expected — the installer is unsigned per Decision 5 in PRD §1.4.

Instruct the user to:

1. Click **More info** in the dialog.
2. Click **Run anyway**.

For silent enterprise deployment via Microsoft Intune or ManageEngine Endpoint Central, push the MSI with `msiexec /i deccan-design-2.0.0.msi /qn`. The silent install bypasses SmartScreen entirely.

## Uninstall

Standard Windows uninstall: **Settings → Apps → deccan-design → Uninstall**.

## Skill harvesting (advanced)

The `deccan-design.wxs` definition installs the top-level `SKILL.md` but does not enumerate `skill/references/` and `skill/assets/` individually. For a production-grade MSI that mirrors the full skill tree:

```powershell
# Generate a WiX fragment from the skill directory tree
heat dir ..\..\skill `
    -gg -srd -dr DeccanSkillDir -cg ClaudeSkillFiles `
    -out skill-fragment.wxs
```

Add `-i skill-fragment.wxs` to the `wix build` invocation in `build.ps1`. The fragment links into the `ClaudeSkill` feature.

## Why no signing step

PRD §1.4 Decision 5 makes signing out of scope. The cost: every first install triggers SmartScreen. The trade: no certificate procurement, no PKCS#12 / EV-cert management, no per-build signing step. The admin guide's "Unsigned-installer support runbook" addresses the user-facing friction.
