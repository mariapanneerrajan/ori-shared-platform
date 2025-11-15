# RPA Build, Install and Launch Script
# ======================================
# This script builds RPA packages, installs them to OpenRV, and launches OpenRV

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RPA Build, Install and Launch Workflow" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build RPA packages
Write-Host "[1/3] Building RPA packages..." -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow
try {
    & "$ScriptDir\build.ps1"
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
        throw "Build script failed with exit code: $LASTEXITCODE"
    }
    Write-Host ""
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Error "Build failed: $_"
    exit 1
}

# Step 2: Install RPA packages to OpenRV
Write-Host "[2/3] Installing RPA packages to OpenRV..." -ForegroundColor Yellow
Write-Host "--------------------------------------------" -ForegroundColor Yellow
try {
    & "$ScriptDir\install.ps1"
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
        throw "Install script failed with exit code: $LASTEXITCODE"
    }
    Write-Host ""
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Error "Installation failed: $_"
    exit 1
}

# Step 3: Launch OpenRV
Write-Host "[3/3] Launching OpenRV..." -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

# OpenRV executable path
$RV_EXE = "C:\OpenRV_1.0\OpenRV_1.0\bin\rv.exe"

# Check if OpenRV executable exists
if (Test-Path $RV_EXE) {
    Write-Host "Starting OpenRV from: $RV_EXE" -ForegroundColor Cyan
    Write-Host ""
    Start-Process -FilePath $RV_EXE
    Write-Host "OpenRV launched successfully!" -ForegroundColor Green
} else {
    Write-Warning "OpenRV executable not found at: $RV_EXE"
    Write-Warning "Please verify the OpenRV installation path and update this script if needed."
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workflow completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
