# Monitoring Dashboard - Quick Start Guide

## Overview
The **Forex Monitoring Dashboard** provides real-time monitoring of your trading system with comprehensive metrics and status updates.

## Features

✅ **System Status** - Module and data file availability  
✅ **Trading Sessions** - Current session status for all pairs  
✅ **Live Prices** - Real-time market prices (EUR/USD, GBP/USD, USD/JPY)  
✅ **Performance Metrics** - Latest backtest results  
✅ **Recent Trades** - Last 5 trades with details  
✅ **Live Trade History** - Real-time trade tracking  

## Quick Start

### Run Dashboard (Single View)
```bash
cd backtesting
python monitoring_dashboard.py
# Choose option 1
```

### Run Dashboard (Auto-Refresh)
```bash
python monitoring_dashboard.py
# Choose option 2 for 60-second refresh
# Choose option 3 for 10-second refresh
```

### Windows Batch File (Optional)
Create `monitor.bat`:
```batch
@echo off
python monitoring_dashboard.py
pause
```

## Dashboard Sections

### 1. System Status
- **[OK]/[X]** Module availability (Session Manager, Data Client)
- **[OK]/[X]** Data file status (backtest summary, trade history, CSV)

### 2. Trading Sessions
For each pair (EURUSD, GBPUSD, USDJPY):
- **[OPEN]/[CLOSED]** Trading recommendation
- Active sessions (Tokyo, London, New York)
- Session overlap detection
- Liquidity score (0-100)
- Trading advice

### 3. Live Prices
Current bid/ask/mid prices for all monitored pairs

### 4. Performance Metrics
From latest backtest:
- Total trades
- Win rate (%)
- Total P&L
- ROI (%)
- Profit factor
- Max drawdown (%)
- Starting/Ending capital

### 5. Recent Trades
Last 5 trades showing:
- Date/time
- Asset
- Direction (BUY/SELL)
- Result ([WIN]/[LOSS])
- P&L amount
- Trading session

### 6. Live Trade History
Real-time tracking of active trades (when telegram bot is running)

## Sample Output

```
====================================================================================================
                        >>> FOREX TRADING SYSTEM - MONITORING DASHBOARD <<<                         
====================================================================================================
                                   Time: 2025-12-04 17:57:54 UTC                                    
====================================================================================================

[+] SYSTEM STATUS
----------------------------------------------------------------------------------------------------
Modules:
  [OK] Session Manager
  [OK] Data Client

Data Files:
  [OK] Backtest Summary
  [OK] Trade History
  [OK] Backtest Csv

[+] TRADING SESSIONS
----------------------------------------------------------------------------------------------------

  EURUSD:
    [OPEN] Status: RECOMMENDED
    Sessions: New York
    Overlap: No overlap
    Liquidity: 85/100
    Advice: GOOD - Acceptable liquidity for this pair

[+] LIVE PRICES
----------------------------------------------------------------------------------------------------
  EURUSD: 1.16620 (Bid: 1.16612, Ask: 1.16627)
  GBPUSD: 1.33560 (Bid: 1.33552, Ask: 1.33567)
  USDJPY: 154.91000 (Bid: 154.90250, Ask: 154.91750)

[+] PERFORMANCE METRICS (Latest Backtest)
----------------------------------------------------------------------------------------------------
  Total Trades: 132
  Win Rate: 94.70%
  Total P&L: $12,451.23
  ROI: 2490.25%
  Profit Factor: 53.39
  Max Drawdown: 95.94%

[+] RECENT TRADES (Latest Backtest)
----------------------------------------------------------------------------------------------------
Date                 Asset      Dir    Win    P&L          Session                       
----------------------------------------------------------------------------------------------------
2025-12-03 15:53:00  GBPUSD     SELL   [LOSS] $    -53.19 London, New York              
2025-11-27 07:45:00  USDJPY     BUY    [WIN]  $    193.73 Tokyo
```

## Usage Tips

### Monitor Before Trading
Run the dashboard before generating signals to check:
- ✅ All modules loaded
- ✅ Current session is optimal
- ✅ Live prices are updating

### Track Performance
Use the dashboard daily to:
- Monitor win rate trends
- Check profit/loss
- Review recent trades
- Ensure system health

### Session Timing
Look for:
- **[OPEN]** status = Good time to trade
- **London/NY Overlap** = Best liquidity
- **Liquidity score 90+** = Optimal

## Customization

### Change Monitored Pairs
Edit `monitoring_dashboard.py`:
```python
# Line ~28
self.pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']  # Add more pairs
```

### Adjust Refresh Rate
```python
# Run with custom interval
dashboard.run(refresh_interval=30)  # 30 seconds
```

### Add More Metrics
Extend the dashboard by adding methods to:
- Track signal generation rate
- Monitor API status
- Display news events
- Show correlation matrix

## Troubleshooting

### "Module not found"
```bash
# Ensure you're in the correct directory
cd backtesting

# Reinstall dependencies
pip install -r requirements.txt
```

### "No backtest data available"
```bash
# Run backtest first
python enhanced_backtest_simulator.py
```

### Pandas Warning
If you see pandas import errors:
```bash
pip install pandas
```

### Screen Won't Clear
Normal behavior on some terminals. The dashboard still works.

## Integration

### With Telegram Bot
The dashboard monitors `trade_history.json` which is updated by the telegram bot. Run both simultaneously:

**Terminal 1:**
```bash
python telegram_bot.py
```

**Terminal 2:**
```bash
python monitoring_dashboard.py
# Choose option 2 (auto-refresh)
```

### With Cron/Task Scheduler
For automated monitoring:

**Linux/macOS (crontab):**
```bash
# Run every hour and save output
0 * * * * cd /path/to/backtesting && python monitoring_dashboard.py > dashboard_log.txt
```

**Windows (Task Scheduler):**
Create task to run `monitoring_dashboard.py` at regular intervals

## Advanced Features

### Export Dashboard to File
```bash
python monitoring_dashboard.py > dashboard_snapshot.txt
# Choose option 1
```

### Create Monitoring Alerts
Modify `monitoring_dashboard.py` to add alerts when:
- Win rate drops below threshold
- New trades are recorded
- System modules fail to load

## Files Used

| File | Purpose |
|------|---------|
| `enhanced_backtest_summary.json` | Performance metrics |
| `enhanced_backtest_1year.csv` | Historical trades |
| `trade_history.json` | Live trade tracking |

## Next Steps

1. ✅ Run dashboard once to verify
2. ✅ Check all modules load correctly
3. ✅ Verify live prices update
4. ✅ Review performance metrics
5. ✅ Use auto-refresh during trading hours

---

**Happy Monitoring! 📊**
