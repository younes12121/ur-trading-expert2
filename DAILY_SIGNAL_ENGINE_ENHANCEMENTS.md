# Daily Signal Engine Enhancements

## Overview
The daily signal engine has been enhanced with comprehensive telemetry, history tracking, analytics, and outcome tracking capabilities.

## 1. Telemetry & Logging Hooks

### Implementation Location
- **File**: `daily_signals_system.py`
- **Method**: `_log_signal_creation()`

### Features
- **Automatic logging** of every signal creation event
- **Structured log data** including:
  - Signal ID (unique identifier)
  - Asset and direction
  - Tier (A_PLUS, A_GRADE, B_GRADE)
  - Quality score
  - Timestamp
  - Trading session
  - Volatility level

### Code Example
```python
def _log_signal_creation(self, signal: Dict):
    """Log signal creation for telemetry and analytics"""
    log_data = {
        'signal_id': signal.get('signal_id'),
        'asset': signal.get('asset'),
        'direction': signal.get('direction'),
        'tier': signal.get('tier'),
        'quality_score': signal.get('quality_score'),
        'timestamp': signal.get('timestamp').isoformat(),
        'session': signal.get('session'),
        'volatility': signal.get('volatility')
    }
    self.logger.info(f"Daily signal created: {log_data}")
```

### Usage
- Logs are automatically created when `generate_daily_signal()` successfully creates a signal
- Logs can be viewed in application logs for debugging and monitoring
- Enables tracking of signal generation patterns and system health

---

## 2. Signal History Tracking

### Implementation Location
- **File**: `daily_signals_system.py`
- **Method**: `_store_signal_history()`
- **Storage**: In-memory list (`self.signal_history`)

### Features
- **Tracks last 1000 signals** (configurable via `max_history_size`)
- **Stores complete signal metadata**:
  - Signal ID
  - Asset, direction, tier
  - Entry, stop loss, take profit prices
  - Quality score
  - Timestamp and session
  - Outcome (initially None, updated when trade closes)
  - P&L (updated when trade closes)

### Code Example
```python
def _store_signal_history(self, signal: Dict):
    """Store signal in history for analytics"""
    history_entry = {
        'signal_id': signal.get('signal_id'),
        'asset': signal.get('asset'),
        'direction': signal.get('direction'),
        'tier': signal.get('tier'),
        'entry_price': signal.get('entry_price'),
        'stop_loss': signal.get('stop_loss'),
        'take_profit_1': signal.get('take_profit_1'),
        'quality_score': signal.get('quality_score'),
        'timestamp': signal.get('timestamp'),
        'session': signal.get('session'),
        'outcome': None,  # Updated when trade closes
        'pnl': None,
        'closed_at': None
    }
    self.signal_history.append(history_entry)
    
    # Auto-prune to keep only last 1000 signals
    if len(self.signal_history) > self.max_history_size:
        self.signal_history = self.signal_history[-self.max_history_size:]
```

### Usage
- History is automatically maintained for all generated signals
- Access via `get_daily_signals_history(limit)` function
- Used by `/daily_history` command in Telegram bot

---

## 3. Analytics Functions

### Implementation Location
- **File**: `daily_signals_system.py`
- **Method**: `get_signal_analytics(days: int = 30)`

### Features
- **Time-based analytics** (default: last 30 days, configurable)
- **Performance metrics**:
  - Total signals generated
  - Closed signals count
  - Wins and losses
  - Win rate percentage
  - Average quality score
- **Distribution analysis**:
  - Tier distribution (A_PLUS, A_GRADE, B_GRADE counts)
  - Asset distribution (which assets were most signaled)

### Code Example
```python
def get_signal_analytics(self, days: int = 30) -> Dict:
    """Get analytics for daily signals over specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_signals = [s for s in self.signal_history 
                     if s.get('timestamp') and s['timestamp'] >= cutoff_date]
    
    # Calculate win rate
    closed_signals = [s for s in recent_signals if s.get('outcome')]
    wins = len([s for s in closed_signals if s.get('outcome') == 'WIN'])
    losses = len([s for s in closed_signals if s.get('outcome') == 'LOSS'])
    win_rate = (wins / total_closed * 100) if total_closed > 0 else 0
    
    # Tier and asset distributions
    tier_dist = {}
    asset_dist = {}
    # ... calculation logic ...
    
    return {
        'total_signals': len(recent_signals),
        'closed_signals': total_closed,
        'wins': wins,
        'losses': losses,
        'win_rate': round(win_rate, 2),
        'avg_quality_score': round(avg_quality, 2),
        'tier_distribution': tier_dist,
        'asset_distribution': asset_dist
    }
```

### Usage
- Called by `/daily_summary` command
- Can be used for performance reporting
- Supports custom time periods (1-90 days)

### Example Output
```python
{
    'total_signals': 45,
    'closed_signals': 38,
    'wins': 32,
    'losses': 6,
    'win_rate': 84.21,
    'avg_quality_score': 87.5,
    'tier_distribution': {
        'A_PLUS': 5,
        'A_GRADE': 25,
        'B_GRADE': 15
    },
    'asset_distribution': {
        'EURUSD': 12,
        'BTC': 8,
        'GOLD': 7,
        ...
    }
}
```

---

## 4. Signal Outcome Tracking

### Implementation Location
- **File**: `daily_signals_system.py`
- **Method**: `update_signal_outcome(signal_id, outcome, pnl)`
- **Integration**: `trade_tracker.py` automatically calls this when trades close

### Features
- **Automatic outcome updates** when trades are closed
- **Three outcome types**:
  - `WIN` - Trade closed profitably
  - `LOSS` - Trade closed at a loss
  - `BREAKEVEN` - Trade closed at zero P&L
- **P&L tracking** - Stores actual profit/loss amount
- **Timestamp tracking** - Records when trade was closed

### Code Example
```python
def update_signal_outcome(self, signal_id: str, outcome: str, pnl: float = None):
    """Update signal outcome when trade is closed"""
    for entry in self.signal_history:
        if entry.get('signal_id') == signal_id:
            entry['outcome'] = outcome  # 'WIN', 'LOSS', 'BREAKEVEN'
            entry['pnl'] = pnl
            entry['closed_at'] = datetime.now()
            break
```

### Integration with Trade Tracker
When a trade is closed in `trade_tracker.py`:
```python
# If this is a daily signal, update the daily signals system
if trade.get('is_daily_signal') and trade.get('signal_id'):
    from daily_signals_system import update_daily_signal_outcome
    outcome = 'WIN' if pnl > 0 else 'LOSS' if pnl < 0 else 'BREAKEVEN'
    update_daily_signal_outcome(trade['signal_id'], outcome, pnl)
```

### Usage
- Automatically tracks performance of daily signals
- Enables accurate win rate calculations
- Used in analytics and reporting
- Visible in `/daily_history` command

---

## Signal ID Generation

Every signal gets a unique ID when created:
```python
signal['signal_id'] = f"DS_{current_time.strftime('%Y%m%d_%H%M%S')}_{self.today_signals}"
```

**Format**: `DS_YYYYMMDD_HHMMSS_N`
- Example: `DS_20241210_143025_3` (3rd signal on Dec 10, 2024 at 14:30:25)

This ID is used to:
- Link signals to trades
- Track outcomes
- Reference signals in analytics
- Display in user commands

---

## Complete Flow

1. **Signal Generation**:
   - `generate_daily_signal()` creates signal
   - Unique `signal_id` is generated
   - Signal is logged via `_log_signal_creation()`
   - Signal is stored in history via `_store_signal_history()`

2. **Signal Delivery**:
   - Signal sent to user via Telegram
   - User can execute trade using signal details
   - Trade can be tracked with `signal_id`

3. **Trade Execution**:
   - Trade added to tracker with `signal_id` and `is_daily_signal=True`
   - Trade tracked in `trade_tracker.py`

4. **Trade Closure**:
   - When trade closes, `update_signal_outcome()` is called
   - Outcome (WIN/LOSS/BREAKEVEN) is recorded
   - P&L is stored
   - Analytics are updated

5. **Analytics & Reporting**:
   - `/daily_history` shows signal history with outcomes
   - `/daily_summary` shows performance analytics
   - All metrics calculated from tracked data

---

## Benefits

1. **Performance Monitoring**: Track actual win rates vs expected
2. **Quality Assurance**: Identify which tiers/assets perform best
3. **User Transparency**: Users can see their signal history and outcomes
4. **System Improvement**: Data-driven optimization of signal generation
5. **Compliance**: Complete audit trail of all signals generated

---

## API Functions

### For Bot Commands
```python
from daily_signals_system import (
    generate_daily_signal,           # Generate new signal
    get_daily_signals_status,        # Get system status
    get_daily_signals_analytics,     # Get performance analytics
    get_daily_signals_history,       # Get signal history
    update_daily_signal_outcome      # Update outcome (auto-called)
)
```

### Example Usage
```python
# Generate signal
signal = generate_daily_signal(account_balance=1000)

# Get analytics
analytics = get_daily_signals_analytics(days=30)

# Get history
history = get_daily_signals_history(limit=10)
```

---

## Configuration

### Adjustable Parameters
- `max_history_size`: Number of signals to keep in history (default: 1000)
- `days` parameter in analytics: Time period for analysis (default: 30)

### Logging
- Uses Python's `logging` module
- Log level: INFO for signal creation
- Can be configured via logging configuration

---

## Future Enhancements

Potential improvements:
1. **Persistent Storage**: Save history to database/file for persistence
2. **Advanced Analytics**: More detailed metrics (Sharpe ratio, max drawdown, etc.)
3. **Real-time Dashboard**: Web interface for signal analytics
4. **Alert System**: Notify when win rate drops below threshold
5. **Export Functionality**: Export analytics to CSV/JSON









