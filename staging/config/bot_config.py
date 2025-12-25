"""
Professional Configuration for Telegram Bot
DO NOT commit this file to GitHub (it contains secrets)
"""

# ============================================================================
# TELEGRAM BOT CONFIGURATION
# ============================================================================

# Get your bot token from @BotFather on Telegram
# Steps:
# 1. Message @BotFather on Telegram
# 2. Send /newbot
# 3. Follow instructions to create bot
# 4. Copy the token below
BOT_TOKEN = "8437677554:AAHUZJf0R1gYHdsAvVEm3u5pOJq50CHXTiY"

# Optional: Restrict bot to specific chat IDs for security
# Leave empty [] to allow all users
ALLOWED_CHAT_IDS = []  # Example: [123456789, 987654321]

# ============================================================================
# AUTO-ALERT SETTINGS
# ============================================================================

# Enable/disable automatic signal alerts
ALERT_ENABLED = True

# How often to check for new signals (in seconds)
# 1800 = 30 minutes
# 3600 = 1 hour
CHECK_INTERVAL = 1800

# Quantum Intraday check interval (faster for intraday signals)
# 300 = 5 minutes
# 600 = 10 minutes
QUANTUM_INTRADAY_CHECK_INTERVAL = 300  # 5 minutes

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Default risk per trade (percentage)
DEFAULT_RISK_PCT = 1.0  # 1% risk per trade

# Default starting capital
DEFAULT_CAPITAL = 500

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

# Enable debug mode (more verbose logging)
DEBUG_MODE = False

# Log file location
LOG_FILE = "telegram_bot.log"

# Maximum number of concurrent API requests
MAX_CONCURRENT_REQUESTS = 5
