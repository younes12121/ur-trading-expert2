@echo off
REM Automated Syntax Checker for telegram_bot.py
REM Run this anytime to check for syntax errors

echo ========================================
echo BOT SYNTAX CHECKER
echo ========================================
echo.

python auto_syntax_checker.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo STATUS: All checks passed!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo STATUS: Issues found - review above
    echo ========================================
)

pause

