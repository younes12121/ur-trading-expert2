"""
Example: Enhanced Backtest Engine Usage
Demonstrates the key features of the institutional-grade backtest engine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest_engine import BacktestEngine, PositionMode, ExecutionPriority
from backtest_analytics import BacktestAnalytics


def generate_sample_data(days=30, start_price=100.0):
    """Generate sample OHLCV data for testing"""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        periods=days * 24 * 12,  # 5-minute candles
        freq='5min'
    )
    
    # Generate realistic price movement
    np.random.seed(42)
    returns = np.random.normal(0, 0.001, len(dates))
    prices = start_price * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * (1 + np.abs(np.random.normal(0, 0.002, len(dates)))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.002, len(dates)))),
        'close': prices,
        'volume': np.random.uniform(1000, 10000, len(dates))
    }, index=dates)
    
    # Ensure OHLC consistency
    data['high'] = data[['high', 'open', 'close']].max(axis=1)
    data['low'] = data[['low', 'open', 'close']].min(axis=1)
    
    return data


def simple_moving_average_strategy(data):
    """Simple moving average crossover strategy"""
    if len(data) < 20:
        return {'direction': 'HOLD'}
    
    sma_fast = data['close'].rolling(window=5).mean()
    sma_slow = data['close'].rolling(window=20).mean()
    
    current_fast = sma_fast.iloc[-1]
    current_slow = sma_slow.iloc[-1]
    prev_fast = sma_fast.iloc[-2] if len(sma_fast) > 1 else current_fast
    prev_slow = sma_slow.iloc[-2] if len(sma_slow) > 1 else current_slow
    
    # Bullish crossover
    if current_fast > current_slow and prev_fast <= prev_slow:
        entry_price = data['close'].iloc[-1]
        return {
            'direction': 'BUY',
            'entry_price': entry_price,
            'stop_loss': entry_price * 0.98,  # 2% stop loss
            'take_profit_1': entry_price * 1.02,  # 2% TP1
            'take_profit_2': entry_price * 1.04,  # 4% TP2
            'symbol': 'BTCUSDT'
        }
    
    # Bearish crossover
    elif current_fast < current_slow and prev_fast >= prev_slow:
        entry_price = data['close'].iloc[-1]
        return {
            'direction': 'SELL',
            'entry_price': entry_price,
            'stop_loss': entry_price * 1.02,  # 2% stop loss
            'take_profit_1': entry_price * 0.98,  # 2% TP1
            'take_profit_2': entry_price * 0.96,  # 4% TP2
            'symbol': 'BTCUSDT'
        }
    
    return {'direction': 'HOLD'}


def add_scenario_tags(data, timestamp):
    """Add scenario tags for performance attribution"""
    tags = {}
    
    # Market volatility regime
    if len(data) >= 20:
        volatility = data['close'].pct_change().tail(20).std()
        if volatility > 0.02:
            tags['regime'] = 'high_volatility'
        elif volatility > 0.01:
            tags['regime'] = 'medium_volatility'
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
    
    # Trend strength
    if len(data) >= 20:
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        current_price = data['close'].iloc[-1]
        trend_strength = abs(current_price - sma_20) / sma_20
        if trend_strength > 0.02:
            tags['trend'] = 'strong'
        else:
            tags['trend'] = 'weak'
    
    return tags


def main():
    """Main example function"""
    print("=" * 70)
    print("Enhanced Backtest Engine Example")
    print("=" * 70)
    print()
    
    # 1. Generate sample data
    print("📊 Step 1: Generating sample data...")
    data = generate_sample_data(days=30, start_price=100.0)
    print(f"   Generated {len(data)} candles")
    print(f"   Period: {data.index[0]} to {data.index[-1]}")
    print()
    
    # 2. Configure backtest engine
    print("⚙️  Step 2: Configuring backtest engine...")
    engine = BacktestEngine(
        initial_capital=10000,
        risk_per_trade=0.01,  # 1% risk per trade
        
        # Execution parameters
        slippage=0.0005,  # 0.05% base slippage
        bid_ask_spread=0.0002,  # 0.02% spread
        fee_entry=0.001,  # 0.1% entry fee
        fee_exit=0.001,  # 0.1% exit fee
        volatility_lookback=20,
        
        # Position management
        max_concurrent_trades=3,
        max_positions_per_symbol=1,
        position_mode=PositionMode.NETTING,
        execution_priority=ExecutionPriority.STOP_LOSS_FIRST,
        
        # Risk limits
        max_daily_loss_pct=5.0,  # Stop if daily loss > 5%
        max_drawdown_pct=20.0,  # Stop if drawdown > 20%
        max_leverage=10.0,  # Max 10x leverage
        
        # Risk-based sizing
        use_atr_sizing=True,
        atr_period=14,
        volatility_factor=1.5,
        
        # Reproducibility
        random_seed=42
    )
    print("   Engine configured with:")
    print(f"   - Initial Capital: ${engine.initial_capital:,.2f}")
    print(f"   - Risk per Trade: {engine.risk_per_trade * 100}%")
    print(f"   - Max Concurrent Trades: {engine.max_concurrent_trades}")
    print(f"   - Max Daily Loss: {engine.max_daily_loss_pct}%")
    print(f"   - Max Drawdown: {engine.max_drawdown_pct}%")
    print()
    
    # 3. Run backtest
    print("🔄 Step 3: Running backtest...")
    engine.run_backtest(
        data,
        simple_moving_average_strategy,
        verbose=True,
        tags_func=add_scenario_tags
    )
    print()
    
    # 4. Get results
    print("📈 Step 4: Extracting results...")
    trades_df = engine.get_trades_df()
    equity_df = engine.get_equity_curve_df()
    
    print(f"   Total Trades: {len(trades_df)}")
    if len(trades_df) > 0:
        print(f"   Winning Trades: {len(trades_df[trades_df['pnl'] > 0])}")
        print(f"   Total P&L: ${trades_df['pnl'].sum():,.2f}")
        print(f"   Total Fees: ${trades_df['total_fees'].sum():,.2f}")
        print(f"   Total Slippage: ${(trades_df['entry_slippage'] + trades_df['exit_slippage']).sum():,.2f}")
    print()
    
    # 5. Generate analytics
    if len(trades_df) > 0:
        print("📊 Step 5: Generating analytics...")
        analytics = BacktestAnalytics(
            trades_df=trades_df,
            equity_curve_df=equity_df,
            initial_capital=engine.initial_capital,
            start_date=data.index[0],
            end_date=data.index[-1]
        )
        
        # Calculate metrics
        metrics = analytics.calculate_all_metrics()
        
        print("   Key Metrics:")
        print(f"   - Total Return: {metrics['total_return_pct']:+.2f}%")
        print(f"   - CAGR: {metrics['cagr']:+.2f}%")
        print(f"   - Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   - Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        print(f"   - Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"   - Profit Factor: {metrics['profit_factor']:.2f}")
        print()
        
        # Generate tearsheet
        print("📄 Step 6: Generating tearsheet report...")
        result = analytics.generate_tearsheet(
            output_dir="backtests",
            filename="example_backtest"
        )
        print(f"   JSON Report: {result['json_path']}")
        print(f"   HTML Report: {result['html_path']}")
        print(f"   CSV Summary: {result['csv_path']}")
        print()
        
        # Print comprehensive report
        analytics.print_comprehensive_report()
    else:
        print("   No trades executed - skipping analytics")
    
    print("=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
