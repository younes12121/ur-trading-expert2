"""
Run Backtest - Main Script
Ties together all components and runs a complete backtest
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Import our modules
from historical_data import HistoricalDataManager
from backtest_engine import BacktestEngine
from performance_metrics import PerformanceMetrics
import config

def simple_strategy(data: pd.DataFrame) -> dict:
    """
    Simple momentum strategy for demonstration
    Replace this with your BTCScalpingAnalyzerV2 signals
    
    Args:
        data: Historical OHLCV data up to current point
    
    Returns:
        Signal dictionary with entry, SL, TP1, TP2
    """
    if len(data) < 20:
        return {'direction': 'HOLD'}
    
    # Simple moving average crossover
    current_price = data['close'].iloc[-1]
    sma_short = data['close'].iloc[-10:].mean()
    sma_long = data['close'].iloc[-20:].mean()
    
    # Calculate volatility for stop loss
    returns = data['close'].pct_change().dropna()
    volatility = returns.std()
    
    # Stop distance based on volatility
    stop_distance = current_price * volatility * 2
    
    # Generate signal
    if sma_short > sma_long:
        direction = 'BUY'
        entry_price = current_price
        stop_loss = entry_price - stop_distance
        tp1 = entry_price + stop_distance * 1.2
        tp2 = entry_price + stop_distance * 2.5
    elif sma_short < sma_long:
        direction = 'SELL'
        entry_price = current_price
        stop_loss = entry_price + stop_distance
        tp1 = entry_price - stop_distance * 1.2
        tp2 = entry_price - stop_distance * 2.5
    else:
        return {'direction': 'HOLD'}
    
    return {
        'direction': direction,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit_1': tp1,
        'take_profit_2': tp2
    }


def run_backtest(days: int = 7, interval: str = "5m", initial_capital: float = 500,
                risk_per_trade: float = 0.01):
    """
    Run complete backtest
    
    Args:
        days: Number of days of historical data
        interval: Timeframe (5m, 15m, 1h, etc.)
        initial_capital: Starting capital
        risk_per_trade: Risk per trade (0.01 = 1%)
    """
    print("=" * 70)
    print("BACKTESTING SYSTEM")
    print("=" * 70)
    print(f"Symbol: BTCUSDT")
    print(f"Timeframe: {interval}")
    print(f"Period: {days} days")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Risk per Trade: {risk_per_trade * 100}%")
    print("=" * 70)
    print()
    
    # Step 1: Download historical data
    print("Step 1: Downloading Historical Data...")
    data_manager = HistoricalDataManager()
    data = data_manager.get_data(interval=interval, days=days, use_cache=True)
    
    if data is None or len(data) == 0:
        print("❌ Failed to download data")
        return
    
        print(f"Downloaded {len(data)} candles")
    print(f"   Period: {data.index[0]} to {data.index[-1]}")
    print()
    
    # Step 2: Run backtest
    print("Step 2: Running Backtest...")
    engine = BacktestEngine(
        initial_capital=initial_capital,
        risk_per_trade=risk_per_trade,
        slippage=0.0005,  # 0.05%
        fee=0.001  # 0.1%
    )
    
    # Use performance mode if enabled in config
    performance_mode = getattr(config, 'PERFORMANCE_MODE', True)
    engine.run_backtest(data, simple_strategy, verbose=False, performance_mode=performance_mode)
    print()
    
    # Step 3: Calculate performance metrics
    print("Step 3: Calculating Performance Metrics...")
    trades_df = engine.get_trades_df()
    equity_df = engine.get_equity_curve_df()
    
    if len(trades_df) > 0:
        print(f"Executed {len(trades_df)} trades")
        print()
        
        # Calculate metrics
        metrics_calc = PerformanceMetrics(trades_df, equity_df, initial_capital)
        metrics_calc.print_report()
        
        # Show sample trades
        print()
        print("=" * 70)
        print("SAMPLE TRADES (First 5)")
        print("=" * 70)
        print(trades_df.head().to_string())
        print()
        
        # Save results
        print("Saving Results...")
        trades_df.to_csv('data_cache/backtest_trades.csv', index=False)
        equity_df.to_csv('data_cache/backtest_equity.csv', index=False)
        print("Saved to data_cache/backtest_trades.csv and backtest_equity.csv")
        
        # Generate visualizations
        print()
        print("Generating Visualizations...")
        from backtest_visualizer import BacktestVisualizer
        
        viz = BacktestVisualizer(trades_df, equity_df, initial_capital)
        report_path = viz.generate_all()
        
        print()
        print("=" * 70)
        print("BACKTEST REPORT READY!")
        print("=" * 70)
        print(f"Open: {report_path}")
        print("=" * 70)
        
    else:
        print("No trades executed")
        print("   Try adjusting strategy parameters or using more data")
    
    print()
    print("=" * 70)
    print("BACKTEST COMPLETE!")
    print("=" * 70)
    
    return engine, trades_df, equity_df


if __name__ == "__main__":
    # Run backtest with default parameters
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  BTC TRADING STRATEGY BACKTEST".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    # You can modify these parameters
    DAYS = 365  # Number of days to backtest (1 YEAR)
    INTERVAL = "5m"  # Timeframe
    CAPITAL = 500  # Initial capital
    RISK = 0.01  # 1% risk per trade
    
    try:
        engine, trades, equity = run_backtest(
            days=DAYS,
            interval=INTERVAL,
            initial_capital=CAPITAL,
            risk_per_trade=RISK
        )
        
        print("\n")
        print("💡 TIP: To use your BTCScalpingAnalyzerV2 strategy:")
        print("   1. Modify the simple_strategy() function in this file")
        print("   2. Import and use your analyzer's generate_trading_signal()")
        print("   3. Run the backtest again")
        print("\n")
        
    except Exception as e:
        print(f"\nError running backtest: {e}")
        import traceback
        traceback.print_exc()
