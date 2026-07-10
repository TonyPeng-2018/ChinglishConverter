# Build a standalone chinglish.exe on Windows (PowerShell).
#
# Usage (from the repo root):
#   ./packaging/build.ps1
#
# Produces dist/chinglish.exe. Run it with .\dist\chinglish.exe --help
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install "pyinstaller>=6.0"

if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist)  { Remove-Item -Recurse -Force dist }

pyinstaller packaging/chinglish.spec

Write-Host ""
Write-Host "Built: dist/chinglish.exe"
Write-Host "Try:   .\dist\chinglish.exe --version"
