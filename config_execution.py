"""
Execution Configuration
Parameters for advanced execution enhancements
"""

# Enhancement 1: Dynamic Entry Optimization
ENTRY_OPTIMIZATION_WINDOW = 15  # minutes to wait for better entry
MAX_ENTRY_SLIPPAGE = 0.005  # 0.5% max slippage from signal price
TIGHT_SPREAD_THRESHOLD = 0.001  # 0.1% bid/ask spread
PULLBACK_MIN = 0.002  # 0.2% minimum pullback
PULLBACK_MAX = 0.005  # 0.5% maximum pullback

# Enhancement 2: Partial Position Scaling
ENTRY_TRANCHES = {
    'immediate': 0.50,  # 50% at signal
    'pullback': 0.30,   # 30% on pullback
    'confirmation': 0.20  # 20% after confirmation
}

EXIT_TARGETS = {
    'tp1': {'percentage': 0.25, 'rr_ratio': 1.5},  # 25% at 1:1.5
    'tp2': {'percentage': 0.50, 'rr_ratio': 2.5},  # 50% at 1:2.5
    'tp3': {'percentage': 0.25, 'rr_ratio': 4.0}   # 25% at 1:4.0
}

# Enhancement 3: Smart Stop Loss Management
MOVE_SL_TO_BREAKEVEN_AFTER_TP1 = True
TRAIL_SL_AFTER_TP2 = True
TRAIL_ATR_MULTIPLIER = 1.5  # Trail at 1.5x ATR
NEVER_MOVE_SL_AGAINST = True  # Never widen stop loss

# Enhancement 4: Time-Based Exit Rules
TIME_EXIT_NO_MOVEMENT_HOURS = 4  # Exit if no 2% move in 4 hours
TIME_EXIT_MOVEMENT_THRESHOLD = 0.02  # 2% movement threshold
EXIT_BEFORE_NEWS_HOURS = 2  # Exit 2 hours before major news
EXIT_FRIDAY_UTC_HOUR = 20  # Close all positions Friday 20:00 UTC
MAX_POSITION_HOURS = 24  # Review positions open >24 hours

# Enhancement 5: Confluence Confirmation Delay
CONFIRMATION_DELAY_MIN = 5  # Wait 5 minutes minimum
CONFIRMATION_DELAY_MAX = 10  # Wait 10 minutes maximum
MAX_PRICE_MOVE_AGAINST = 0.01  # 1% max move against signal
RECHECK_ALL_CRITERIA = True  # Re-validate all 17 criteria
MIN_CONFIDENCE_AFTER_DELAY = 70  # Minimum confidence after delay

# General Execution Settings
USE_LIMIT_ORDERS = True  # Use limit orders for better fills
LIMIT_ORDER_OFFSET = 0.001  # 0.1% better than market
MAX_ORDER_WAIT_MINUTES = 5  # Cancel unfilled limit orders after 5 min
FALLBACK_TO_MARKET = True  # Use market order if limit not filled

# Risk Management
MAX_SLIPPAGE_TOLERANCE = 0.01  # 1% max slippage tolerance
REQUIRE_VOLUME_CONFIRMATION = True  # Require volume spike
MIN_VOLUME_MULTIPLIER = 1.2  # 1.2x average volume
