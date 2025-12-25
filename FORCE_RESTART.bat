@echo off
echo Killing all Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 >nul
echo.
echo Starting bot with Stripe payments...
cd /d "%~dp0"
python telegram_bot.py














