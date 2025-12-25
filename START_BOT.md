# How to Start the Bot

## If the bot won't open or closes immediately:

### Option 1: Use the batch file (Windows)
Double-click `start_bot.bat` - this will keep the window open so you can see any errors.

### Option 2: Run from command prompt
1. Open Command Prompt or PowerShell
2. Navigate to the bot directory:
   ```
   cd "C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting"
   ```
3. Run the bot:
   ```
   python telegram_bot.py
   ```

### Option 3: Use the diagnostic script first
Run this to check if everything is set up correctly:
```
python test_bot_startup.py
```

### Option 4: Use the wrapper script (captures all output)
```
python run_bot.py
```
This will create a log file with all output and errors.

## Common Issues:

1. **Bot closes immediately**: 
   - Check if BOT_TOKEN is set in `bot_config.py`
   - Run `python test_bot_startup.py` to diagnose
   - Check the log file created by `run_bot.py`

2. **Import errors**:
   - Make sure all required files exist
   - Check that all Python packages are installed: `pip install python-telegram-bot`

3. **No output**:
   - The bot might be running but not showing output
   - Check if the bot is actually running in the background
   - Use `run_bot.py` to capture all output to a file

## What to check:

1. ✅ BOT_TOKEN is set in `bot_config.py`
2. ✅ All required Python packages are installed
3. ✅ All required files exist (signal_api.py, etc.)
4. ✅ Internet connection is working
5. ✅ No firewall blocking Telegram API












