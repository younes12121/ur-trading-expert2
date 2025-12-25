"""
Configuration file for BTC trading bot

IMPORTANT: This bot fetches data from Binance (BTCUSDT) and generates signals
for TradingView CFD BTCUSD trading.

The SIGNALS (BUY/SELL direction, stop loss %, take profit %) are valid
for your TradingView BTCUSD CFD.
"""

# Binance API Configuration (for data fetching only)
BINANCE_API_KEY = ""  # Add your Binance API key here (optional for public data)
BINANCE_API_SECRET = ""  # Add your Binance API secret here (optional for public data)

# Trading Configuration
SYMBOL = "BTCUSDT"  # Data source: Binance
TRADING_SYMBOL = "BTCUSD"  # Your TradingView CFD symbol
TIMEFRAME = "5m"  # 1m, 5m, 15m, 1h, etc.
CAPITAL = 500  # Your trading capital in USD
RISK_PER_TRADE = 0.01  # 1% risk per trade
LOT_SIZE = 0.02  # Default lot size

# Risk Management
MAX_DAILY_LOSS = 0.05  # 5% max daily loss
MAX_OPEN_POSITIONS = 1  # Maximum concurrent positions
LEVERAGE = 1  # Leverage (1 = no leverage, spot trading)

# API Endpoints
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_TESTNET_URL = "https://testnet.binance.vision"  # For testing
USE_TESTNET = False  # Set to False for live trading data (Recommended for analysis)

# Data Settings
HISTORICAL_DAYS = 365  # Days of historical data to fetch (1 year)
CACHE_DURATION = 60  # Cache duration in seconds

# Alert Settings
ENABLE_ALERTS = False  # Enable Telegram/Email alerts
TELEGRAM_BOT_TOKEN = ""  # Your Telegram bot token
TELEGRAM_CHAT_ID = ""  # Your Telegram chat ID

# Database
DB_PATH = "trades.db"  # SQLite database path

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "trading_bot.log"
