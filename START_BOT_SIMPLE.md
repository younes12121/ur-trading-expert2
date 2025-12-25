# 🚀 How to Start Your Bot - Simple Guide

## ✅ Good News: Logs Are Working!

Your `logs\app.log` file exists and shows the bot has started before. The logging system is working correctly!

---

## 🎯 How to Start the Bot

### Method 1: Command Line (Recommended)

1. **Open PowerShell or Command Prompt**

2. **Navigate to bot directory:**
   ```powershell
   cd "C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting"
   ```

3. **Start the bot:**
   ```powershell
   python telegram_bot.py
   ```

4. **You should see:**
   ```
   [OK] Production monitoring enabled
   [OK] Configuration loaded from bot_config.py
   Starting ENHANCED Ultimate Signal Bot...
   Bot is running with AUTO-ALERTS!
   ✅ Production monitoring: ENABLED
   ```

5. **Keep this window open** - The bot runs in this window

6. **To stop:** Press `Ctrl+C`

---

### Method 2: Using Batch File (Easier)

If you have `start_bot.bat`:

1. **Double-click** `start_bot.bat`
2. Bot starts automatically!

---

## 📊 How to View Logs

### View Logs While Bot is Running

**Option 1: PowerShell (Recommended)**
```powershell
# View last 20 lines
Get-Content logs\app.log -Tail 20

# Watch logs in real-time (like tail -f)
Get-Content logs\app.log -Wait -Tail 10
```

**Option 2: Notepad**
```powershell
notepad logs\app.log
```

**Option 3: Command Prompt**
```cmd
type logs\app.log | more
```

---

## 🔍 What Logs Tell You

### `logs\app.log` - Main Log
- ✅ Command executions
- ✅ Bot startup messages
- ✅ General information

### `logs\errors.log` - Errors Only
- ❌ Errors and exceptions
- ⚠️ Warnings

### `logs\performance.log` - Performance
- ⚡ Execution times
- 📊 Performance metrics

---

## ✅ Quick Test

1. **Start bot:**
   ```powershell
   python telegram_bot.py
   ```

2. **In Telegram, send:**
   ```
   /start
   ```

3. **Check logs:**
   ```powershell
   Get-Content logs\app.log -Tail 5
   ```

4. **You should see:**
   ```
   2025-12-08 XX:XX:XX - trading_bot - INFO - {"command": "start", "user_id": XXXX, "success": true}
   ```

---

## ⚠️ Common Issues

### Bot Won't Start?

**Check 1: Is Python installed?**
```powershell
python --version
```

**Check 2: Is bot_config.py correct?**
- Make sure `BOT_TOKEN` is set
- File should be in same directory

**Check 3: Are dependencies installed?**
```powershell
pip install -r requirements.txt
```

**Check 4: Is another bot instance running?**
- Close all Python windows
- Check Task Manager for `python.exe` processes

### Logs Not Updating?

- Make sure bot is actually running
- Check if logs directory is writable
- Try restarting the bot

### Can't See Logs?

- Logs are created automatically when bot starts
- If `logs\` folder doesn't exist, bot creates it
- Check file permissions

---

## 🎯 What "logs\app.log won't start" Means

If you meant:
- **"Bot won't start"** → Follow "Bot Won't Start?" section above
- **"Can't view logs"** → Use `Get-Content logs\app.log` command
- **"Logs are empty"** → Bot hasn't run commands yet, send `/start` in Telegram

---

## 📝 Quick Reference

```powershell
# Start bot
python telegram_bot.py

# View logs (last 20 lines)
Get-Content logs\app.log -Tail 20

# View errors
Get-Content logs\errors.log

# Watch logs live
Get-Content logs\app.log -Wait -Tail 10
```

---

## ✅ Your Bot is Ready!

The logging system is working. Just start the bot and test it in Telegram!

**Next:** Send `/start` to your bot and check the logs to see it working! 🚀

