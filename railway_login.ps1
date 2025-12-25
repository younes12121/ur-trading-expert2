# Railway CLI Login Helper for PowerShell
# Run this script: .\railway_login.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Railway CLI Login" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if railway.exe exists
if (-not (Test-Path "railway-cli\railway.exe")) {
    Write-Host "ERROR: Railway CLI not found!" -ForegroundColor Red
    Write-Host "Please download it first." -ForegroundColor Red
    exit 1
}

Write-Host "Railway CLI found. Starting login..." -ForegroundColor Green
Write-Host "This will open your browser for authentication." -ForegroundColor Yellow
Write-Host ""

# Execute railway login
& .\railway-cli\railway.exe login

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Login successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. .\railway-cli\railway.exe init" -ForegroundColor White
    Write-Host "  2. .\railway-cli\railway.exe add postgresql" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Login failed. Please try again." -ForegroundColor Red
}

