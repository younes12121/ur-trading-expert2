# Telegram Bot Setup - Quick Start

## 🚀 Quick Start (3 Minutes)

###Step 1: Create Your Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name: `UR Trading Expert` (or any name you want)
4. Choose a username: `ur_trading_expert_bot` (must end with `bot`)
5. Copy the token you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Bot

1. Open `bot_config.py` in your editor
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual token
3. Save the file

### Step 3: Run the Bot

```bash
cd backtesting
python telegram_bot.py
```

Or use the batch file:
```bash
start_bot.bat
```

### Step 4: Test the Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Try `/help` to see all commands

---

## 📱 Available Commands

### Signals
- `/signal` - Get BTC & Gold signals
- `/forex` - Get Forex overview
- `/signals` - Get ALL signals (Crypto + Gold + Forex)
- `/btc` - Detailed BTC analysis
- `/gold` - Detailed Gold analysis
- `/eurusd` - EUR/USD professional analysis
- `/gbpusd` - GBP/USD professional analysis
- `/usdjpy` - USD/JPY professional analysis

### Trading
- `/risk [balance]` - Calculate position size
- `/capital [amount]` - Set trading capital
- `/opentrade` - Open a trade for tracking
- `/closetrade` - Close a tracked trade
- `/trades` - View open trades
- `/performance` - View performance stats

### System
- `/status` - Check system status
- `/alerts` - Toggle auto-alerts on/off
- `/chart` - Get TradingView chart links
- `/stats` - View backtest statistics
- `/help` - Show all commands

---

## 🔔 Auto-Alerts Feature

The bot automatically checks for new signals every 30 minutes and sends you alerts when:
- New BTC ELITE A+ signal detected
- New GOLD ELITE A+ signal detected
- New FOREX ELITE A+ signal detected

To enable/disable for your chat:
```
/alerts
```

---

## 🛡️ Security Tips

1. **Never share your bot token**
2. **Keep bot_config.py private** (don't commit to GitHub)
3. **Optional**: Restrict bot to specific users by adding chat IDs to `ALLOWED_CHAT_IDS` in `bot_config.py`

To get your chat ID:
1. Message @userinfobot on Telegram
2. Copy your ID
3. Add to `ALLOWED_CHAT_IDS = [your_id_here]` in `bot_config.py`

---

## 📊 Example Usage

### Get EUR/USD Signal
```
You: /eurusd

Bot: 🔍 Analyzing EUR/USD...

💱 EUR/USD SIGNAL

Price: 1.08542
Confidence: 65.0%
Progress: 70.6%
Criteria: 12/17

❌ No signal yet

Key Failures:
• Low confidence (65/100)
• Weak confluence
• Suboptimal session
```

### Track a Trade
```
You: /opentrade EURUSD BUY 1.0850 1.0800 1.0900 1.0950 0.01

Bot: ✅ TRADE #1 OPENED!

Asset: EURUSD
Direction: BUY
Entry: $1.09
Stop Loss: $1.08
TP1: $1.09
TP2: $1.10
Position Size: 0.01

📏 PIP ANALYSIS:
SL: 50 pips
TP1: 50 pips (R:R 1:1.0)
TP2: 100 pips (R:R 1:2.0)
```

---

## ⚙️ Configuration Options

Edit `bot_config.py` to customize:

```python
# Enable/disable auto-alerts
ALERT_ENABLED = True

# Check interval (seconds)
CHECK_INTERVAL = 1800  # 30 minutes

# Restrict to specific users (optional)
ALLOWED_CHAT_IDS = []  # Leave empty to allow all

# Default risk per trade
DEFAULT_RISK_PCT = 1.0  # 1%

# Default starting capital
DEFAULT_CAPITAL = 500
```

---

## 🔧 Troubleshooting

### Bot doesn't respond
- Check bot token is correct in `bot_config.py`
- Make sure bot is running (terminal should show "Bot is running")
- Try stopping and restarting the bot

### "Unauthorized" error
- Bot token is incorrect
- Get a new token from @BotFather

### Commands not working
- Make sure you're using `/` before command
- Check command spelling
- Try `/help` to see available commands

### No signals showing
- This is NORMAL! ELITE A+ signals are RARE
- The system has strict 17-20 criteria filters
- Expected frequency: 1-3 signals per week per asset
- Be patient and wait for TRUE quality setups

---

## 🚀 Running 24/7

### Option 1: Local Computer
Keep terminal open, bot runs continuously

### Option 2: Cloud Server (Recommended)
Deploy to Railway, Heroku, or VPS

**Railway (Free tier available):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Option 3: Windows Task Scheduler
Schedule `start_bot.bat` to run at startup

---

## 📈 Features

✅ **Multi-Asset Support** - BTC, Gold, EUR/USD, GBP/USD, USD/JPY  
✅ **ELITE A+ Filter** - 17-20 strict criteria  
✅ **Auto-Alerts** - Instant notifications for new signals  
✅ **Trade Tracking** - Track your trades and performance  
✅ **Risk Calculator** - Proper position sizing  
✅ **Professional Analysis** - Session timing, correlation, news  
✅ **TradingView Integration** - Direct chart links  

---

## 💡 Pro Tips

1. **Enable Auto-Alerts** - Never miss a signal
2. **Set Your Capital** - Use `/capital` for accurate risk calculation
3. **Track Trades** - Use `/opentrade` and `/closetrade` for performance tracking
4. **Check Status** - Use `/status` to see current market conditions
5. **Be Patient** - Elite signals are rare but high-quality

---

## 🆘 Need Help?

1. Send `/help` to the bot
2. Check `DEPLOYMENT_GUIDE.md` for detailed setup
3. Review `README.md` for system overview

---

**Your bot is ready! Start with `/start` on Telegram** 🚀
