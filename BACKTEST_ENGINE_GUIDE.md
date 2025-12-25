# Enhanced Backtest Engine Guide

## Overview

The enhanced backtest engine provides institutional-grade backtesting capabilities with realistic execution modeling, comprehensive risk management, and detailed analytics.

## Key Features

### 1. Realistic Execution Modeling
- **Bid/Ask Spread**: Models real market spreads
- **Volatility-Aware Slippage**: Slippage increases with market volatility
- **Per-Side Fees**: Separate entry and exit fees
- **Adaptive Slippage**: Adjusts based on market conditions

### 2. Portfolio Risk Management
- **Max Concurrent Trades**: Limit number of simultaneous positions
- **Daily Loss Limits**: Stop trading if daily loss exceeds threshold
- **Max Drawdown Protection**: Automatic stop on excessive drawdown
- **Leverage Limits**: Control maximum leverage
- **Per-Asset Capital Caps**: Limit exposure per asset

### 3. Advanced Position Sizing
- **ATR-Based Sizing**: Use Average True Range for dynamic position sizing
- **Volatility-Adjusted**: Adjust size based on market volatility
- **Risk-Based**: Position size based on stop loss distance

### 4. Comprehensive Analytics
- **Performance Metrics**: CAGR, Sharpe, Sortino, Calmar ratios
- **Risk Metrics**: Max drawdown, volatility, downside deviation
- **Cost Analysis**: Fees, slippage, cost drag
- **Tearsheet Reports**: HTML, JSON, and CSV exports

## Basic Usage

### Simple Backtest

```python
from backtest_engine import BacktestEngine
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'open': [100, 101, 102],
    'high': [101, 102, 103],
    'low': [99, 100, 101],
    'close': [100.5, 101.5, 102.5],
    'volume': [1000, 1100, 1200]
}, index=pd.date_range('2024-01-01', periods=3, freq='5min'))

# Define strategy
def my_strategy(data):
    if len(data) < 2:
        return {'direction': 'HOLD'}
    
    # Simple momentum strategy
    if data['close'].iloc[-1] > data['close'].iloc[-2]:
        return {
            'direction': 'BUY',
            'entry_price': data['close'].iloc[-1],
            'stop_loss': data['close'].iloc[-1] * 0.98,
            'take_profit_1': data['close'].iloc[-1] * 1.02,
            'take_profit_2': data['close'].iloc[-1] * 1.04,
            'symbol': 'BTCUSDT'
        }
    return {'direction': 'HOLD'}

# Run backtest
engine = BacktestEngine(
    initial_capital=1000,
    risk_per_trade=0.01,  # 1% risk per trade
    slippage=0.0005,      # 0.05% slippage
    fee=0.001            # 0.1% fee
)

engine.run_backtest(data, my_strategy, verbose=True)

# Get results
trades_df = engine.get_trades_df()
equity_df = engine.get_equity_curve_df()
```

## Advanced Configuration

### Enhanced Execution Parameters

```python
engine = BacktestEngine(
    initial_capital=10000,
    risk_per_trade=0.02,
    
    # Execution parameters
    slippage=0.0005,           # Base slippage
    bid_ask_spread=0.0002,     # 0.02% spread
    fee_entry=0.001,          # Entry fee (0.1%)
    fee_exit=0.001,           # Exit fee (0.1%)
    volatility_lookback=20,    # Periods for volatility calc
    
    # Position management
    max_concurrent_trades=5,
    max_positions_per_symbol=2,
    position_mode=PositionMode.NETTING,  # or HEDGING
    
    # Execution priority
    execution_priority=ExecutionPriority.STOP_LOSS_FIRST,
    
    # Risk limits
    max_daily_loss_pct=5.0,    # Stop if daily loss > 5%
    max_drawdown_pct=20.0,     # Stop if drawdown > 20%
    max_leverage=10.0,         # Max 10x leverage
    per_asset_cap_pct=0.2,     # Max 20% capital per asset
    
    # Risk-based sizing
    use_atr_sizing=True,
    atr_period=14,
    volatility_factor=1.5,
    
    # Reproducibility
    random_seed=42
)
```

### Scenario Tagging

Add tags to trades for performance attribution:

```python
def tags_function(data, timestamp):
    """Add scenario tags to trades"""
    tags = {}
    
    # Market regime
    volatility = data['close'].pct_change().std()
    if volatility > 0.02:
        tags['regime'] = 'high_volatility'
    else:
        tags['regime'] = 'low_volatility'
    
    # Trading session
    hour = timestamp.hour
    if 8 <= hour < 16:
        tags['session'] = 'london'
    elif 13 <= hour < 21:
        tags['session'] = 'new_york'
    else:
        tags['session'] = 'asian'
    
    return tags

engine.run_backtest(data, strategy_func, tags_func=tags_function)
```

## Analytics and Reporting

### Generate Comprehensive Report

```python
from backtest_analytics import BacktestAnalytics
from datetime import datetime

# After running backtest
trades_df = engine.get_trades_df()
equity_df = engine.get_equity_curve_df()

# Create analytics
analytics = BacktestAnalytics(
    trades_df=trades_df,
    equity_curve_df=equity_df,
    initial_capital=1000,
    start_date=data.index[0],
    end_date=data.index[-1]
)

# Calculate all metrics
metrics = analytics.calculate_all_metrics()
print(f"CAGR: {metrics['cagr']:.2f}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")

# Generate tearsheet
result = analytics.generate_tearsheet(
    output_dir="backtests",
    filename="my_backtest"
)

# Print comprehensive report
analytics.print_comprehensive_report()
```

### Available Metrics

**Performance Metrics:**
- Total Return, CAGR
- Win Rate, Profit Factor
- Average Win/Loss, Expectancy
- Best/Worst Trade

**Risk Metrics:**
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Max Drawdown, Max Drawdown Duration
- Volatility, Downside Deviation

**Cost Metrics:**
- Total Fees, Total Slippage
- Cost Drag Percentage
- Average Cost per Trade

**Trade Metrics:**
- Average Trade Duration
- TP1/TP2 Hit Rates
- Exit Reason Breakdown
- Consecutive Wins/Losses
- Exposure Time

## Execution Assumptions

### Order Execution Priority

The engine supports different execution priorities:

1. **STOP_LOSS_FIRST** (default): Stop losses are checked first for risk management
2. **TAKE_PROFIT_FIRST**: Take profits are checked first
3. **FIFO**: First-in-first-out order checking

### Intrabar Execution

- Stop losses and take profits are checked against high/low of each candle
- If a level is touched within a candle, the order is executed
- Slippage is applied based on volatility and order type

### Partial Fills

- TP1 closes 50% of position
- Stop loss moved to breakeven after TP1
- TP2 closes remaining 50%
- Fees and slippage applied to each partial close

## Risk Management

### Daily Loss Limit

```python
engine = BacktestEngine(
    max_daily_loss_pct=5.0  # Stop trading if daily loss > 5%
)
```

When daily loss limit is reached:
- Trading is disabled for the rest of the day
- Open positions remain open
- Equity curve continues to be tracked

### Max Drawdown Protection

```python
engine = BacktestEngine(
    max_drawdown_pct=20.0  # Stop trading if drawdown > 20%
)
```

When max drawdown is reached:
- Trading is permanently disabled
- Open positions remain open
- Equity curve continues to be tracked

### Leverage Limits

```python
engine = BacktestEngine(
    max_leverage=10.0  # Maximum 10x leverage
)
```

Position size is automatically reduced if it would exceed leverage limit.

## Position Sizing Methods

### Fixed Risk (Default)

Position size based on fixed risk percentage:

```python
engine = BacktestEngine(
    risk_per_trade=0.01  # Risk 1% per trade
)
```

### ATR-Based Sizing

Use Average True Range for dynamic sizing:

```python
engine = BacktestEngine(
    use_atr_sizing=True,
    atr_period=14,
    volatility_factor=1.5  # Use 1.5x ATR for stop distance
)
```

## Testing

Run the test suite:

```bash
pytest test_backtest_engine.py -v
```

Tests cover:
- Trade creation and management
- Position sizing calculations
- Fee and slippage modeling
- Risk limit enforcement
- Analytics calculations
- Tearsheet generation

## Best Practices

1. **Use Realistic Parameters**: Set slippage, fees, and spreads based on your broker
2. **Test Risk Limits**: Verify daily loss and drawdown limits work as expected
3. **Use Scenario Tagging**: Tag trades by market regime, session, etc. for analysis
4. **Review Cost Analysis**: Check if fees/slippage are eating into profits
5. **Validate with Small Data**: Test with small datasets before full backtests
6. **Use Random Seeds**: Set `random_seed` for reproducible results
7. **Check Equity Curve**: Review drawdown periods and recovery

## Example: Complete Backtest Workflow

```python
from backtest_engine import BacktestEngine
from backtest_analytics import BacktestAnalytics
import pandas as pd

# 1. Load historical data
data = load_historical_data('BTCUSDT', '5m', days=365)

# 2. Define strategy
def my_strategy(data):
    # Your strategy logic here
    pass

# 3. Configure engine
engine = BacktestEngine(
    initial_capital=10000,
    risk_per_trade=0.01,
    max_daily_loss_pct=5.0,
    max_drawdown_pct=20.0,
    use_atr_sizing=True,
    random_seed=42
)

# 4. Run backtest
engine.run_backtest(data, my_strategy, verbose=True)

# 5. Get results
trades_df = engine.get_trades_df()
equity_df = engine.get_equity_curve_df()

# 6. Analyze results
analytics = BacktestAnalytics(
    trades_df=trades_df,
    equity_curve_df=equity_df,
    initial_capital=10000,
    start_date=data.index[0],
    end_date=data.index[-1]
)

# 7. Generate report
analytics.generate_tearsheet(output_dir="backtests")
analytics.print_comprehensive_report()
```

## Troubleshooting

### No Trades Executed
- Check if strategy returns valid signals
- Verify capital is sufficient for position size
- Check if risk limits are preventing trades

### Unrealistic Results
- Verify slippage and fee parameters
- Check if data quality is good
- Review execution assumptions

### Performance Issues
- Reduce data size for testing
- Disable verbose mode
- Use smaller lookback periods

## API Reference

See docstrings in `backtest_engine.py` and `backtest_analytics.py` for detailed API documentation.
