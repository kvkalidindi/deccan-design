#Requires -Version 5.1
<#
.SYNOPSIS
    Configures the new Outlook (Windows / Mac) Deccan signature.

.DESCRIPTION
    Reads the unconfigured signature template installed by the deccan-design
    MSI, prompts for Name / Role / Email / Phone, substitutes the placeholders,
    and writes a configured signature to the Outlook signatures directory.

    Idempotent — running again overwrites the previous configuration.

.NOTES
    Part of deccan-design v2.0. Repository:
    https://github.com/kvkalidindi/deccan-design
#>

[CmdletBinding()]
param(
    [string]$Name,
    [string]$Role,
    [string]$Email,
    [string]$Phone,
    [string]$SignaturesDir = (Join-Path $env:APPDATA 'Microsoft\Signatures')
)

$ErrorActionPreference = 'Stop'

function Read-NonEmpty([string]$Prompt, [string]$Existing) {
    if ($Existing) { return $Existing }
    do {
        $val = Read-Host -Prompt $Prompt
        if ([string]::IsNullOrWhiteSpace($val)) {
            Write-Host "  Value is required." -ForegroundColor Yellow
        }
    } while ([string]::IsNullOrWhiteSpace($val))
    return $val.Trim()
}

Write-Host ""
Write-Host "deccan-design v2.0 — Outlook signature configuration" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------"
Write-Host ""

# 1. Locate template
$HtmlTemplate = Join-Path $SignaturesDir 'deccan-signature-template.htm'
$TxtTemplate  = Join-Path $SignaturesDir 'deccan-signature-template.txt'

if (-not (Test-Path $HtmlTemplate)) {
    Write-Error @"
Could not find the deccan-design signature template at:
  $HtmlTemplate

Has the deccan-design MSI been installed? Re-run the installer and try again,
or specify a different signatures directory with -SignaturesDir.
"@
}

# 2. Collect inputs
$Name  = Read-NonEmpty -Prompt 'Your full name'    -Existing $Name
$Role  = Read-NonEmpty -Prompt 'Your role / title' -Existing $Role
$Email = Read-NonEmpty -Prompt 'Your work email'   -Existing $Email
$Phone = Read-NonEmpty -Prompt 'Office line'       -Existing $Phone

# 3. Substitute
function Expand-Template([string]$Path) {
    $raw = Get-Content -Path $Path -Raw
    $out = $raw
    $out = $out -replace '\{\{NAME\}\}',  [System.Net.WebUtility]::HtmlEncode($Name)
    $out = $out -replace '\{\{ROLE\}\}',  [System.Net.WebUtility]::HtmlEncode($Role)
    $out = $out -replace '\{\{EMAIL\}\}', [System.Net.WebUtility]::HtmlEncode($Email)
    $out = $out -replace '\{\{PHONE\}\}', [System.Net.WebUtility]::HtmlEncode($Phone)
    return $out
}

# Plain text template uses raw substitution (no HTML escaping)
function Expand-Plain([string]$Path) {
    $raw = Get-Content -Path $Path -Raw
    $out = $raw
    $out = $out -replace '\{\{NAME\}\}',  $Name
    $out = $out -replace '\{\{ROLE\}\}',  $Role
    $out = $out -replace '\{\{EMAIL\}\}', $Email
    $out = $out -replace '\{\{PHONE\}\}', $Phone
    return $out
}

$HtmlOut = Join-Path $SignaturesDir 'Deccan.htm'
$TxtOut  = Join-Path $SignaturesDir 'Deccan.txt'

(Expand-Template -Path $HtmlTemplate) | Out-File -FilePath $HtmlOut -Encoding utf8 -Force
if (Test-Path $TxtTemplate) {
    (Expand-Plain -Path $TxtTemplate) | Out-File -FilePath $TxtOut -Encoding utf8 -Force
}

# 4. Report
Write-Host ""
Write-Host "Wrote:" -ForegroundColor Green
Write-Host "  $HtmlOut"
if (Test-Path $TxtOut) { Write-Host "  $TxtOut" }
Write-Host ""
Write-Host "Next step in new Outlook:" -ForegroundColor Cyan
Write-Host "  Settings (gear icon) -> Accounts -> Signatures."
Write-Host "  Select 'Deccan' as the default for new messages and replies/forwards."
Write-Host ""
