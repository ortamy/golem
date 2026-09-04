# clean-smoke.ps1 - full reset of smoke environment and sequential rerun (workers=1)
# Usage: powershell -ExecutionPolicy Bypass -File tools\clean-smoke.ps1

$ErrorActionPreference = 'Continue'
$Root   = Split-Path -Parent $PSScriptRoot
$Lab    = Join-Path $Root 'products\website\apps\researchlab'
$ShotDir = Join-Path $Lab 'tests\screenshots'
$JsonFile = Join-Path $Lab 'test-results\smoke.json'
$LastRun = Join-Path $Lab 'test-results\.last-run.json'

Write-Host '[clean-smoke] 1/3 Kill stuck smoke processes...'
Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -match 'chrome|headless_shell|msedge') -and
    ($_.CommandLine -match 'playwright test tests/smoke|smoke.spec') -and
    ($_.CommandLine -notmatch 'playwright-mcp')
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "  killed $($_.ProcessId) $($_.Name)"
}
Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -match 'node|cmd') -and
    ($_.CommandLine -match 'playwright test tests/smoke|smoke.spec.js --workers')
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "  killed $($_.ProcessId) $($_.Name)"
}
Get-NetTCPConnection -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  freed port 4173 ($($_.OwningProcess))"
}
Start-Sleep -Seconds 2

Write-Host '[clean-smoke] 2/3 Clean artifacts...'
Get-ChildItem $ShotDir -Filter *.png -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Remove-Item $JsonFile -Force -ErrorAction SilentlyContinue
Remove-Item $LastRun -Force -ErrorAction SilentlyContinue
Write-Host "  png left: $((Get-ChildItem $ShotDir -Filter *.png -ErrorAction SilentlyContinue).Count)"
Write-Host "  smoke.json exists: $(Test-Path $JsonFile)"

Write-Host '[clean-smoke] 3/3 Run full smoke (workers=1)...'
Push-Location $Lab
try {
    npm run test:smoke -- --workers=1
    $Code = $LASTEXITCODE
    Write-Host "[clean-smoke] npm finished rc=$Code"
} finally {
    Pop-Location
}

Write-Host '[clean-smoke] RESULT:'
if (Test-Path $JsonFile) {
    $stats = (Get-Content $JsonFile -Raw | ConvertFrom-Json).stats
    Write-Host "  tests=$($stats.expected) passed=$($stats.expected) failed=$($stats.unexpected) skipped=$($stats.skipped) flaky=$($stats.flaky)"
} else {
    Write-Host '  smoke.json NOT created'
}
$pngCount = (Get-ChildItem $ShotDir -Filter *.png -ErrorAction SilentlyContinue).Count
Write-Host "  png=$pngCount"