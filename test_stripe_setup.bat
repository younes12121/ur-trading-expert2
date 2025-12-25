@echo off
REM Quick Stripe Setup Test Script for Windows
REM Run this after setting up .env file

echo ========================================
echo  STRIPE SETUP TEST SCRIPT
echo ========================================
echo.

REM Check if .env file exists
echo [1/4] Checking for .env file...
if exist .env (
    echo       ✓ .env file found
) else (
    echo       ✗ .env file NOT found!
    echo       Create .env file first - see .env.template
    goto :error
)
echo.

REM Check Python is available
echo [2/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo       ✗ Python not found!
    goto :error
) else (
    python --version
    echo       ✓ Python is installed
)
echo.

REM Run setup checker
echo [3/4] Running Stripe configuration checker...
echo.
python check_stripe_setup.py
if %errorlevel% neq 0 (
    echo.
    echo       ✗ Setup incomplete - review errors above
    goto :error
)
echo.

REM Run payment handler test
echo [4/4] Testing payment handler...
echo.
python payment_handler.py
if %errorlevel% neq 0 (
    echo.
    echo       ✗ Payment handler test failed
    goto :error
)
echo.

echo ========================================
echo  ✓ ALL TESTS PASSED!
echo ========================================
echo.
echo Your Stripe setup is COMPLETE! 🎉
echo.
echo Next steps:
echo   1. Start your bot: python telegram_bot.py
echo   2. Test /subscribe in Telegram
echo   3. Use test card: 4242 4242 4242 4242
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo  ✗ SETUP INCOMPLETE
echo ========================================
echo.
echo See these guides for help:
echo   - STRIPE_ACTION_PLAN.md
echo   - COMPLETE_STRIPE_NOW.md
echo.
pause
exit /b 1



