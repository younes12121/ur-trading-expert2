@echo off
echo Stopping all running Python processes (including Telegram bot)...
echo.

taskkill /F /IM python.exe

echo.
echo All Python processes stopped.
echo You can now run the bot again with: python telegram_bot.py
pause
