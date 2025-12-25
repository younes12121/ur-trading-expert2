@echo off
echo Fixing .env file name...
cd /d "%~dp0"
if exist "notepad.env" (
    copy "notepad.env" ".env"
    echo ✓ Created .env file successfully!
    del "notepad.env"
    echo ✓ Removed notepad.env
    echo.
    echo Testing Stripe setup...
    python check_stripe_setup.py
) else (
    echo notepad.env not found!
)
pause

