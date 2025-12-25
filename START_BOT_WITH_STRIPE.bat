@echo off
echo ============================================
echo  Starting UR Trading Bot with Stripe
echo ============================================
echo.
echo Checking configuration...
python check_stripe_setup.py
echo.
echo Starting bot...
echo.
python telegram_bot.py
pause

