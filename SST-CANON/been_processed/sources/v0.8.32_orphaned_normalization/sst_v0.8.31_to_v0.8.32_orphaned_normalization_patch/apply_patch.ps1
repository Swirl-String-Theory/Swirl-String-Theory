param(
    [Parameter(Position=0)]
    [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$PatchDir = Join-Path $Here "patches"

$Main = Join-Path $Root "SST_CANON-v0.8.31.tex"
$RT = Join-Path $Root "SST_CANON-v0.8.31-research-track.tex"

foreach ($File in @($Main, $RT)) {
    if (-not (Test-Path -LiteralPath $File)) {
        throw "Missing source file: $File"
    }
}

function Assert-Sha256([string]$File, [string]$Expected) {
    $Actual = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) {
        throw "SHA-256 mismatch for $File`nExpected: $Expected`nActual:   $Actual"
    }
}

Assert-Sha256 $Main "06c7f5bacfde31d1503bc45de8e7854946b56924c4c18551ecb99d05402f55b3"
Assert-Sha256 $RT "312e87055334681add3b680284d0e9a50063fce7b13c689386aa6b4e4335b18c"

$OutMain = Join-Path $Root "SST_CANON-v0.8.32.tex"
$OutRT = Join-Path $Root "SST_CANON-v0.8.32-research-track.tex"

Copy-Item -LiteralPath $Main -Destination $OutMain -Force
Copy-Item -LiteralPath $RT -Destination $OutRT -Force

if (-not (Get-Command patch -ErrorAction SilentlyContinue)) {
    throw "GNU patch was not found in PATH. Run this script from Git Bash/WSL, or install patch.exe."
}

& patch $OutMain -i (Join-Path $PatchDir "0001-main-canon-orphaned-normalization.diff")
if ($LASTEXITCODE -ne 0) { throw "Main Canon patch failed." }

& patch $OutRT -i (Join-Path $PatchDir "0002-research-track-provenance-scaling-audit.diff")
if ($LASTEXITCODE -ne 0) { throw "Research Track patch failed." }

Write-Host "Created:"
Write-Host "  $OutMain"
Write-Host "  $OutRT"
