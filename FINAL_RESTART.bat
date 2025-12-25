@echo off
cls
echo ============================================
echo   FINAL DEBUG RESTART WITH FULL LOGGING
echo ============================================
echo.
echo Killing all Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 3 >nul
echo.
echo Starting bot with detailed Stripe logging...
echo.
cd /d "%~dp0"
python telegram_bot.py
pause














