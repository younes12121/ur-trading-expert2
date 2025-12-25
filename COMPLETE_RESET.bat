@echo off
color 0A
cls
echo ========================================
echo   COMPLETE BOT RESET WITH STRIPE
echo ========================================
echo.
echo [1/5] Killing ALL Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 3 >nul
echo       Done!
echo.
echo [2/5] Checking Stripe configuration...
cd /d "%~dp0"
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('   Stripe Key:', 'FOUND' if os.getenv('STRIPE_SECRET_KEY') else 'MISSING')"
echo.
echo [3/5] Testing payment handler...
python -c "from payment_handler import PaymentHandler; p=PaymentHandler(); print('   Stripe Configured:', p.is_configured())"
echo.
echo [4/5] Starting bot with Stripe payments...
echo.
echo ========================================
echo   BOT STARTING - WATCH FOR MESSAGES
echo ========================================
echo.
python telegram_bot.py
echo.
echo [5/5] Bot stopped.
pause














