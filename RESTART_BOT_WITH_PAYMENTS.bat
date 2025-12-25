@echo off
echo ========================================
echo  RESTARTING BOT WITH STRIPE PAYMENTS
echo ========================================
echo.
echo ✅ Auto-generated Checkout URLs: ENABLED
echo ✅ Payment Success Handler: ENABLED
echo ✅ All Stripe features: ACTIVE
echo.
echo Starting bot...
echo.
cd /d "%~dp0"
python telegram_bot.py
pause

