param(
    [string]$Version = "dev"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $root "dist"
$releaseDir = Join-Path $root "release"
$archiveName = "ScanLine-$Version-win64.zip"
$archivePath = Join-Path $releaseDir $archiveName

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

pyinstaller --clean --noconfirm "$root\ScanLine.spec"

if (-not (Test-Path "$distDir\ScanLine\ScanLine.exe")) {
    throw "Build failed: dist\\ScanLine\\ScanLine.exe was not created."
}

if (Test-Path $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

Compress-Archive -Path "$distDir\ScanLine\*" -DestinationPath $archivePath -Force

Write-Host "Build complete:"
Write-Host "  EXE: $distDir\ScanLine\ScanLine.exe"
Write-Host "  ZIP: $archivePath"
