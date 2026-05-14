#Requires -Version 5.1
<#
.SYNOPSIS
    Render a deccan-design HTML document to PDF via Edge or Chrome headless,
    and optionally verify the page structure.

.DESCRIPTION
    Build / QA helper for the deccan-design v2.0 system. Not part of the
    installer payload; not pushed to endpoints.

    The deccan-design CSS encodes a strict print contract: cover on one page
    with no footer, body pages with footers, end page on one page with no
    footer, every H1 on a new page. This script renders an HTML deliverable
    to PDF and (with -Verify) checks each page against the contract.

.PARAMETER InputHtml
    Path to the source HTML file. Required.

.PARAMETER Output
    Path to write the PDF. Defaults to the input path with .pdf substituted
    for .html.

.PARAMETER Browser
    'edge' or 'chrome'. Defaults to edge. Falls back to chrome if edge is
    not present.

.PARAMETER Verify
    Run pdftotext against the rendered PDF and report:
      - Total page count.
      - Per-page footer presence (cover and end page should NOT have one;
        body pages should).
      - First textual line per page (useful to confirm H1 placement).
    Requires pdftotext (ships with Git for Windows at
    'C:\Program Files\Git\mingw64\bin\pdftotext.exe').

.PARAMETER OpenAfter
    Open the produced PDF in the default viewer after rendering.

.EXAMPLE
    .\Render-DeccanDocumentPdf.ps1 .\my-memo.html -Verify

.EXAMPLE
    .\Render-DeccanDocumentPdf.ps1 `
        ..\_handoff\skill-smoke-test\python-pilot-verification-v6.html `
        -Verify -OpenAfter

.NOTES
    deccan-design v2.0. Repository:
    https://github.com/kvkalidindi/deccan-design
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputHtml,

    [string]$Output,

    [ValidateSet('edge', 'chrome')]
    [string]$Browser = 'edge',

    [switch]$Verify,

    [switch]$OpenAfter
)

$ErrorActionPreference = 'Stop'

# --- Resolve paths ---------------------------------------------------------

if (-not (Test-Path -LiteralPath $InputHtml)) {
    Write-Error "Input HTML not found: $InputHtml"
}
$inputAbs = (Resolve-Path -LiteralPath $InputHtml).Path

if (-not $Output) {
    $Output = [System.IO.Path]::ChangeExtension($inputAbs, '.pdf')
}
$outAbs = [System.IO.Path]::GetFullPath($Output)

# --- Locate browser --------------------------------------------------------

$candidates = @{
    edge   = @(
        "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
    )
    chrome = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )
}

function Find-Browser([string]$name) {
    foreach ($p in $candidates[$name]) { if (Test-Path $p) { return $p } }
    return $null
}

$browserExe = Find-Browser $Browser
if (-not $browserExe) {
    Write-Warning "$Browser not found; trying the alternative."
    $alt = if ($Browser -eq 'edge') { 'chrome' } else { 'edge' }
    $browserExe = Find-Browser $alt
    if (-not $browserExe) { Write-Error "Neither Edge nor Chrome found." }
    $Browser = $alt
}

# --- Render ----------------------------------------------------------------

$inputUri = 'file:///' + ($inputAbs -replace '\\', '/')
$ud = Join-Path $env:TEMP "deccan-render-$([guid]::NewGuid().ToString('N'))"

try {
    Write-Host "Rendering $inputAbs"
    Write-Host "  via $Browser ($browserExe)"
    Write-Host "  to $outAbs"

    $proc = Start-Process -FilePath $browserExe -ArgumentList @(
        '--headless=new',
        '--disable-gpu',
        "--user-data-dir=$ud",
        '--no-pdf-header-footer',
        "--print-to-pdf=$outAbs",
        $inputUri
    ) -Wait -PassThru -WindowStyle Hidden

    if ($proc.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $outAbs)) {
        Write-Error "$Browser headless render failed (exit $($proc.ExitCode))."
    }

    $pdf = Get-Item -LiteralPath $outAbs
    Write-Host ("  done - {0:N0} bytes" -f $pdf.Length)
}
finally {
    if (Test-Path -LiteralPath $ud) {
        Remove-Item -Recurse -Force -LiteralPath $ud -ErrorAction SilentlyContinue
    }
}

# --- Optional verification ------------------------------------------------

if ($Verify) {
    $pdftotext = @(
        'C:\Program Files\Git\mingw64\bin\pdftotext.exe',
        'C:\Program Files (x86)\Git\mingw64\bin\pdftotext.exe',
        (Get-Command pdftotext.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1)
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    if (-not $pdftotext) {
        Write-Warning "pdftotext.exe not found - skipping verification. Install Git for Windows or add pdftotext to PATH."
    }
    else {
        $tmp = Join-Path $env:TEMP "deccan-verify-$([guid]::NewGuid().ToString('N')).txt"
        & $pdftotext -layout $outAbs $tmp 2>&1 | Out-Null

        $raw = Get-Content -LiteralPath $tmp -Raw
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue

        $pages = $raw -split "`f"
        # pdftotext appends a form-feed after the last page too, producing an
        # empty trailing entry - drop it.
        if ($pages[-1].Trim() -eq '') { $pages = $pages[0..($pages.Length - 2)] }

        Write-Host ""
        Write-Host "=== Page verification ($($pages.Count) pages) ==="

        $footerPattern = 'Deccan Fine Chemicals.{1,3}Confidential'

        for ($i = 0; $i -lt $pages.Count; $i++) {
            $pageNo = $i + 1
            $body = $pages[$i]
            $hasFooter = $body -match $footerPattern

            # First non-blank textual line
            $firstLine = ($body -split "`n" | Where-Object { $_.Trim() -ne '' } | Select-Object -First 1).Trim()
            if ($firstLine.Length -gt 60) { $firstLine = $firstLine.Substring(0, 60) + '...' }

            $isCover = $pageNo -eq 1
            $isEnd   = $pageNo -eq $pages.Count
            $expectFooter = -not ($isCover -or $isEnd)

            $pass = ($hasFooter -eq $expectFooter)
            $tag  = if ($pass) { 'OK ' } else { 'FAIL' }
            $role = if ($isCover) { 'cover' } elseif ($isEnd) { 'end'   } else { 'body ' }
            $foot = if ($hasFooter) { 'has footer' } else { 'no footer ' }

            $color = if ($pass) { 'Green' } else { 'Red' }
            Write-Host ("  [{0}] page {1} ({2}): {3} | first line: {4}" -f $tag, $pageNo, $role, $foot, $firstLine) -ForegroundColor $color
        }

        $failures = 0
        for ($i = 0; $i -lt $pages.Count; $i++) {
            $isCover = ($i -eq 0)
            $isEnd   = ($i -eq $pages.Count - 1)
            $expect  = -not ($isCover -or $isEnd)
            $actual  = ($pages[$i] -match $footerPattern)
            if ($expect -ne $actual) { $failures++ }
        }
        Write-Host ""
        if ($failures -eq 0) {
            Write-Host "Verification PASSED." -ForegroundColor Green
        } else {
            Write-Host "Verification FAILED: $failures page(s) with wrong footer state." -ForegroundColor Red
            exit 1
        }
    }
}

if ($OpenAfter) { Invoke-Item -LiteralPath $outAbs }
