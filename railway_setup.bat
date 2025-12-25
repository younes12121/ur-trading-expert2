@echo off
REM Railway CLI Helper Script for Windows
REM This script helps you run Railway commands easily

echo ========================================
echo Railway CLI Setup Helper
echo ========================================
echo.

REM Check if railway.exe exists
if not exist "railway-cli\railway.exe" (
    echo ERROR: Railway CLI not found!
    echo Please download it first.
    pause
    exit /b 1
)

echo Railway CLI found: railway-cli\railway.exe
echo.

REM Add railway-cli to PATH for this session
set PATH=%CD%\railway-cli;%PATH%

echo Available commands:
echo   1. railway login          - Login to Railway (opens browser)
echo   2. railway init           - Initialize Railway project
echo   3. railway add postgresql - Add PostgreSQL database
echo   4. railway variables      - View environment variables
echo   5. railway up             - Deploy to Railway
echo   6. railway logs           - View deployment logs
echo.

echo To use Railway CLI, run commands like:
echo   .\railway-cli\railway.exe login
echo   .\railway-cli\railway.exe init
echo.

REM If user provided a command, run it
if "%1"=="" (
    echo Run this script with a command, or use .\railway-cli\railway.exe directly
    echo Example: railway_setup.bat login
    pause
    exit /b 0
)

echo Running: .\railway-cli\railway.exe %*
.\railway-cli\railway.exe %*

pause
