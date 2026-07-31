param(
    [string]$MainBase = "SST_CANON-v0.8.30.tex",
    [string]$ResearchBase = "SST_CANON-v0.8.30-research-track.tex"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$MainOut = "SST_CANON-v0.8.31.tex"
$ResearchOut = "SST_CANON-v0.8.31-research-track.tex"

foreach ($f in @($MainBase, $ResearchBase)) {
    if (-not (Test-Path $f)) { throw "Missing base file: $f" }
}
foreach ($f in @($MainOut, $ResearchOut)) {
    if (Test-Path $f) { throw "Refusing to overwrite: $f" }
}
if (-not (Get-Command patch -ErrorAction SilentlyContinue)) {
    throw "GNU patch must be available on PATH."
}

Get-Content -Raw "$Root/patches/0001-main-canon-quasistatic-response-guard.diff" |
    patch --dry-run --batch $MainBase
Get-Content -Raw "$Root/patches/0002-research-track-rotor-participation-audit.diff" |
    patch --dry-run --batch $ResearchBase

Get-Content -Raw "$Root/patches/0001-main-canon-quasistatic-response-guard.diff" |
    patch --batch -o $MainOut $MainBase
Get-Content -Raw "$Root/patches/0002-research-track-rotor-participation-audit.diff" |
    patch --batch -o $ResearchOut $ResearchBase

Write-Host "Created: $MainOut"
Write-Host "Created: $ResearchOut"
