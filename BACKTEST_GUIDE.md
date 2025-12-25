# Backtesting System - Quick Guide

## 🎯 What You Have Now

A complete backtesting framework to test your trading strategy on historical data!

## 📁 New Files Created

1. **historical_data.py** - Downloads BTC price data from Binance
2. **backtest_engine.py** - Simulates trades with TP1/TP2, SL, fees
3. **performance_metrics.py** - Calculates win rate, Sharpe ratio, drawdown
4. **run_backtest.py** - Main script to run everything

## 🚀 How to Run

### Quick Test (Simple Strategy)

```bash
python run_backtest.py
```

This will:
- Download 7 days of 5-minute BTC data
- Run a simple moving average strategy
- Show you complete performance metrics
- Save results to CSV files

### Expected Output

```
📊 PERFORMANCE REPORT
═══════════════════════════════════════════════════════════
Total Trades:           15
Winning Trades:         8
Losing Trades:          7
Win Rate:               53.3%

Initial Capital:        $500.00
Final Capital:          $523.45
Total P&L:              +$23.45
Total Return:           +4.69%

Sharpe Ratio:           1.23
Max Drawdown:           -2.5%
TP1 Hit Rate:           60.0%
TP2 Hit Rate:           40.0%
═══════════════════════════════════════════════════════════
```

## 📊 What It Tests

### Trade Execution
- ✅ Entry at signal price (with slippage)
- ✅ Stop loss monitoring
- ✅ TP1 - Close 50% at first target
- ✅ TP2 - Close remaining 50% at second target
- ✅ Move SL to breakeven after TP1 hits
- ✅ Trading fees (0.1% per trade)

### Performance Metrics
- **Basic**: Win rate, profit factor, total return
- **Risk**: Sharpe ratio, Sortino ratio, max drawdown
- **Trade Analysis**: Average duration, TP hit rates, exit reasons
- **Streaks**: Consecutive wins/losses

## 🔧 Customization

### Change Parameters

Edit `run_backtest.py`:

```python
DAYS = 30  # Test on 30 days instead of 7
INTERVAL = "15m"  # Use 15-minute candles
CAPITAL = 1000  # Start with $1000
RISK = 0.02  # Risk 2% per trade
```

### Use Your Real Strategy

Replace the `simple_strategy()` function with your analyzer:

```python
from btc_analyzer_v2 import BTCScalpingAnalyzerV2

def your_strategy(data: pd.DataFrame) -> dict:
    analyzer = BTCScalpingAnalyzerV2(capital=500, risk_per_trade=0.01)
    
    # Your analyzer needs current market data
    # You'll need to adapt it to work with historical data
    signal = analyzer.generate_trading_signal()
    
    return {
        'direction': signal['direction'],
        'entry_price': signal['entry_price'],
        'stop_loss': signal['stop_loss'],
        'take_profit_1': signal['take_profit_1'],
        'take_profit_2': signal['take_profit_2']
    }
```

## 📈 Results Files

After running, check `data_cache/` folder:

- **backtest_trades.csv** - All trades with entry/exit/P&L
- **backtest_equity.csv** - Equity curve over time
- **BTCUSDT_5m_cache.csv** - Cached price data

## 🎯 Next Steps

### Phase 3 Remaining:
- [ ] Parameter optimization (find best settings)
- [ ] Visual charts (equity curve, drawdown)

### Phase 4: Signal Optimization
- [ ] Test different signal thresholds
- [ ] Multi-timeframe confirmation
- [ ] Adaptive parameters

## 💡 Tips

1. **Start with short periods** (7 days) to test quickly
2. **Check win rate** - should be >50% ideally
3. **Watch max drawdown** - keep it under 10%
4. **TP1 hit rate** - should be >60% for good strategy
5. **Sharpe ratio** - above 1.0 is good, above 2.0 is excellent

## ⚠️ Important Notes

**Backtest Limitations:**
- Past performance ≠ future results
- Slippage in real trading may vary
- Market conditions change
- Overfitting risk if you optimize too much

**Realistic Expectations:**
- 50-60% win rate is good
- 5-10% monthly return is excellent
- Max drawdown under 15% is healthy

## 🆘 Troubleshooting

**"No trades executed"**
- Strategy might be too conservative
- Try more days of data
- Adjust signal thresholds

**"Failed to download data"**
- Check internet connection
- Binance API might be rate-limited
- Wait a minute and try again

**"Module not found"**
- Make sure you're in the right directory
- All files should be in the same folder

---

**Your backtesting system is ready!** 🎉

Test it with the simple strategy first, then integrate your real analyzer.
