# Build script for GLA Calculator using PyInstaller
# Usage: Open PowerShell in project folder and run: .\build.ps1

# Ensure script stops on error
$ErrorActionPreference = 'Stop'

# You can change these variables if needed
$AppName = "GLA Calculator"
$MainScript = "app.py"
$Icon = "icon.ico"
$Assets = "assets"

Write-Host "Building $AppName..."

# Create assets argument. For Windows add-data uses ';' as separator
if (Test-Path $Assets) {
    $dataArg = "--add-data `"$Assets;$Assets`""
} else {
    $dataArg = ""
}

# Run PyInstaller
$cmd = "pyinstaller --onefile --windowed --icon=$Icon $dataArg $MainScript"
Write-Host "Running: $cmd"
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build finished. Output in dist\$MainScript (rename accordingly)." -ForegroundColor Green
} else {
    Write-Error "PyInstaller failed with exit code $LASTEXITCODE"
}
