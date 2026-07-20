param([string]$Target = ".")
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Copy-Item "$Root\BASE\SST_CANON-v0.8.20.tex" "$Target\SST_CANON-v0.8.20.tex" -Force
Copy-Item "$Root\BASE\SST_CANON-v0.8.20-research-track.tex" "$Target\SST_CANON-v0.8.20-research-track.tex" -Force
Get-ChildItem "$Root\patches\*.diff" | Sort-Object Name | ForEach-Object {
  Write-Host "Applying $($_.Name)"
  Push-Location $Target
  git apply --check $_.FullName
  if ($LASTEXITCODE -ne 0) { throw "Patch check failed: $($_.Name)" }
  git apply $_.FullName
  if ($LASTEXITCODE -ne 0) { throw "Patch apply failed: $($_.Name)" }
  Pop-Location
}
