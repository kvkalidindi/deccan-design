#Requires -Version 5.1
<#
.SYNOPSIS
    Builds the deccan-design v2.0 MSI.

.DESCRIPTION
    Runs `wix build` against deccan-design.wxs. Produces an unsigned
    per-user MSI at .\deccan-design-2.0.0.msi.

    Requires WiX Toolset v4 installed (https://wixtoolset.org/docs/).
    The MSI is intentionally unsigned per Decision 5 in PRD §1.4.

.NOTES
    Run from this directory on a Windows build PC.
#>

[CmdletBinding()]
param(
    [string]$Configuration = 'Release',
    [string]$Output        = 'deccan-design-2.0.0.msi'
)

$ErrorActionPreference = 'Stop'

# 1. Verify wix is available
$wix = Get-Command wix -ErrorAction SilentlyContinue
if (-not $wix) {
    Write-Error @"
WiX Toolset v4 is not installed (or not on PATH).

Install with:
  dotnet tool install --global wix

or via the standalone installer from https://wixtoolset.org/docs/.
"@
}

# 2. Ensure WixUI extension is available
& wix extension add -g WixToolset.UI.wixext 2>&1 | Out-Null

# 3. Generate the preferences reminder file
Push-Location $PSScriptRoot
try {
    $reminder = @"
Action required: configure Claude.ai personal preferences.

deccan-design v2.0 is installed, but Claude.ai personal preferences cannot
be configured server-side by the installer. Please paste the text from:

  https://github.com/kvkalidindi/deccan-design/blob/main/claude/personal-preferences.md

into Claude.ai -> Settings -> Profile -> Preferences. One-click navigation:

  https://claude.ai/settings

The local copy of the preferences text is at:
  %APPDATA%\deccan-design\docs\personal-preferences.md

This is a one-time configuration per Claude.ai account.

deccan-design v2.0  ·  Repository: https://github.com/kvkalidindi/deccan-design
"@
    Set-Content -Path 'preferences-reminder.txt' -Value $reminder -Encoding utf8

    # 4. Build
    Write-Host "Building deccan-design MSI ..." -ForegroundColor Cyan
    & wix build `
        deccan-design.wxs `
        -ext WixToolset.UI.wixext `
        -o $Output

    if ($LASTEXITCODE -ne 0) {
        Write-Error "wix build failed with exit code $LASTEXITCODE."
    }

    Write-Host ""
    Write-Host "Built: $((Get-Item $Output).FullName)" -ForegroundColor Green
    Write-Host ""
    Write-Host "The MSI is UNSIGNED. On install the user will see:" -ForegroundColor Yellow
    Write-Host "  'Windows protected your PC' (SmartScreen)."
    Write-Host "  Instruct the user to click 'More info' -> 'Run anyway'."
    Write-Host ""
    Write-Host "For silent enterprise deployment (Intune / Endpoint Central):" -ForegroundColor Cyan
    Write-Host "  msiexec /i $Output /qn"
}
finally {
    Pop-Location
}
