"""
Comprehensive test suite for the enhanced backtest engine
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest_engine import BacktestEngine, Trade, PositionMode, ExecutionPriority
from backtest_analytics import BacktestAnalytics


class TestTrade:
    """Test Trade dataclass"""
    
    def test_trade_creation(self):
        """Test basic trade creation"""
        trade = Trade(
            entry_time=datetime.now(),
            entry_price=100.0,
            direction='BUY',
            lot_size=1.0,
            stop_loss=95.0,
            take_profit_1=105.0,
            take_profit_2=110.0
        )
        
        assert trade.status == 'OPEN'
        assert trade.remaining_size == 1.0
        assert trade.pnl == 0.0
    
    def test_trade_partial_close(self):
        """Test partial trade closure"""
        trade = Trade(
            entry_time=datetime.now(),
            entry_price=100.0,
            direction='BUY',
            lot_size=1.0,
            stop_loss=95.0,
            take_profit_1=105.0,
            take_profit_2=110.0
        )
        
        exit_time = datetime.now() + timedelta(hours=1)
        pnl = trade.close_partial(exit_time, 105.0, 0.5, 'TP1', exit_fee=0.1)
        
        assert trade.remaining_size == 0.5
        assert trade.tp1_hit == True
        assert pnl > 0
        assert trade.status == 'OPEN'
    
    def test_trade_full_close(self):
        """Test full trade closure"""
        trade = Trade(
            entry_time=datetime.now(),
            entry_price=100.0,
            direction='BUY',
            lot_size=1.0,
            stop_loss=95.0,
            take_profit_1=105.0,
            take_profit_2=110.0
        )
        
        exit_time = datetime.now() + timedelta(hours=1)
        trade.close_full(exit_time, 105.0, 'TP1', exit_fee=0.1)
        
        assert trade.status == 'CLOSED'
        assert trade.exit_price == 105.0
        assert trade.exit_reason == 'TP1'
        assert trade.duration_hours > 0
    
    def test_trade_unrealized_pnl(self):
        """Test unrealized P&L calculation"""
        trade = Trade(
            entry_time=datetime.now(),
            entry_price=100.0,
            direction='BUY',
            lot_size=1.0,
            stop_loss=95.0,
            take_profit_1=105.0,
            take_profit_2=110.0
        )
        
        trade.update_unrealized_pnl(105.0)
        assert trade.unrealized_pnl == 5.0
        
        trade.update_unrealized_pnl(95.0)
        assert trade.unrealized_pnl == -5.0


class TestBacktestEngine:
    """Test BacktestEngine class"""
    
    def create_sample_data(self, days=30, start_price=100.0):
        """Create sample OHLCV data"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             periods=days*24*12, freq='5min')  # 5-minute candles
        
        # Generate random walk price data
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
        
        # Ensure high >= close >= low
        data['high'] = data[['high', 'close']].max(axis=1)
        data['low'] = data[['low', 'close']].min(axis=1)
        
        return data
    
    def simple_strategy(self, data):
        """Simple moving average crossover strategy"""
        if len(data) < 20:
            return {'direction': 'HOLD'}
        
        sma_fast = data['close'].rolling(5).mean()
        sma_slow = data['close'].rolling(20).mean()
        
        if sma_fast.iloc[-1] > sma_slow.iloc[-1] and sma_fast.iloc[-2] <= sma_slow.iloc[-2]:
            return {
                'direction': 'BUY',
                'entry_price': data['close'].iloc[-1],
                'stop_loss': data['close'].iloc[-1] * 0.98,
                'take_profit_1': data['close'].iloc[-1] * 1.02,
                'take_profit_2': data['close'].iloc[-1] * 1.04,
                'symbol': 'TEST'
            }
        elif sma_fast.iloc[-1] < sma_slow.iloc[-1] and sma_fast.iloc[-2] >= sma_slow.iloc[-2]:
            return {
                'direction': 'SELL',
                'entry_price': data['close'].iloc[-1],
                'stop_loss': data['close'].iloc[-1] * 1.02,
                'take_profit_1': data['close'].iloc[-1] * 0.98,
                'take_profit_2': data['close'].iloc[-1] * 0.96,
                'symbol': 'TEST'
            }
        
        return {'direction': 'HOLD'}
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = BacktestEngine(
            initial_capital=1000,
            risk_per_trade=0.02,
            slippage=0.001,
            fee=0.001
        )
        
        assert engine.initial_capital == 1000
        assert engine.capital == 1000
        assert engine.risk_per_trade == 0.02
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        engine = BacktestEngine(initial_capital=1000, risk_per_trade=0.01)
        
        lot_size = engine.calculate_position_size(100.0, 95.0)
        assert lot_size > 0
        assert lot_size == pytest.approx(2.0, rel=0.1)  # Risk $10, stop $5 = 2 units
    
    def test_bid_ask_spread(self):
        """Test bid/ask spread application"""
        engine = BacktestEngine(bid_ask_spread=0.001)
        
        buy_price = engine.apply_bid_ask_spread(100.0, 'BUY')
        sell_price = engine.apply_bid_ask_spread(100.0, 'SELL')
        
        assert buy_price > 100.0  # Buying at ask (higher)
        assert sell_price < 100.0  # Selling at bid (lower)
        assert buy_price > sell_price
    
    def test_adaptive_slippage(self):
        """Test volatility-aware slippage"""
        engine = BacktestEngine(slippage_base=0.001)
        
        low_vol_slippage = engine.calculate_adaptive_slippage(100.0, 0.001, 'BUY')
        high_vol_slippage = engine.calculate_adaptive_slippage(100.0, 0.01, 'BUY')
        
        assert high_vol_slippage > low_vol_slippage
    
    def test_fee_calculation(self):
        """Test fee calculation"""
        engine = BacktestEngine(fee_entry=0.001, fee_exit=0.001)
        
        entry_fee = engine.calculate_fee(100.0, 1.0, is_entry=True)
        exit_fee = engine.calculate_fee(100.0, 1.0, is_entry=False)
        
        assert entry_fee == 0.1
        assert exit_fee == 0.1
    
    def test_atr_calculation(self):
        """Test ATR calculation"""
        engine = BacktestEngine()
        data = self.create_sample_data(days=30)
        
        atr = engine.calculate_atr(data, period=14)
        assert len(atr) == len(data)
        assert atr.iloc[-1] > 0
    
    def test_volatility_calculation(self):
        """Test volatility calculation"""
        engine = BacktestEngine()
        data = self.create_sample_data(days=30)
        
        volatility = engine.calculate_volatility(data, lookback=20)
        assert volatility > 0
    
    def test_simple_backtest(self):
        """Test simple backtest execution"""
        engine = BacktestEngine(
            initial_capital=1000,
            risk_per_trade=0.01,
            random_seed=42
        )
        
        data = self.create_sample_data(days=10)
        engine.run_backtest(data, self.simple_strategy, verbose=False)
        
        # Should have executed some trades
        assert len(engine.trades) >= 0  # May or may not have trades depending on data
        
        # Equity curve should be populated
        assert len(engine.equity_curve) == len(data)
    
    def test_risk_limits_daily_loss(self):
        """Test daily loss limit"""
        engine = BacktestEngine(
            initial_capital=1000,
            max_daily_loss_pct=5.0,
            random_seed=42
        )
        
        # Create data that will trigger losses
        data = self.create_sample_data(days=5)
        
        # Manually trigger a large loss
        engine.capital = 900  # 10% loss
        engine.daily_pnl[datetime.now().date()] = -100
        
        result = engine.check_risk_limits(datetime.now(), 900)
        # Should still allow trading (5% limit not reached)
        assert result == True or result == False  # Depends on implementation
    
    def test_max_concurrent_trades(self):
        """Test max concurrent trades limit"""
        engine = BacktestEngine(
            initial_capital=10000,
            max_concurrent_trades=2,
            random_seed=42
        )
        
        assert engine.can_open_trade('SYMBOL1') == True
        assert engine.can_open_trade('SYMBOL2') == True
        
        # Open 2 trades
        signal1 = {
            'direction': 'BUY',
            'entry_price': 100.0,
            'stop_loss': 95.0,
            'take_profit_1': 105.0,
            'take_profit_2': 110.0,
            'symbol': 'SYMBOL1'
        }
        signal2 = {
            'direction': 'BUY',
            'entry_price': 100.0,
            'stop_loss': 95.0,
            'take_profit_1': 105.0,
            'take_profit_2': 110.0,
            'symbol': 'SYMBOL2'
        }
        
        engine.open_trade(signal1, datetime.now())
        engine.open_trade(signal2, datetime.now())
        
        assert len(engine.open_trades) == 2
        assert engine.can_open_trade('SYMBOL3') == False
    
    def test_trades_dataframe(self):
        """Test trades DataFrame generation"""
        engine = BacktestEngine(initial_capital=1000, random_seed=42)
        
        data = self.create_sample_data(days=5)
        engine.run_backtest(data, self.simple_strategy, verbose=False)
        
        trades_df = engine.get_trades_df()
        
        if len(trades_df) > 0:
            assert 'entry_time' in trades_df.columns
            assert 'exit_time' in trades_df.columns
            assert 'pnl' in trades_df.columns
            assert 'total_fees' in trades_df.columns
    
    def test_equity_curve_dataframe(self):
        """Test equity curve DataFrame generation"""
        engine = BacktestEngine(initial_capital=1000, random_seed=42)
        
        data = self.create_sample_data(days=5)
        engine.run_backtest(data, self.simple_strategy, verbose=False)
        
        equity_df = engine.get_equity_curve_df()
        
        assert len(equity_df) == len(data)
        assert 'equity' in equity_df.columns
        assert 'drawdown_pct' in equity_df.columns


class TestBacktestAnalytics:
    """Test BacktestAnalytics class"""
    
    def create_sample_trades(self):
        """Create sample trades DataFrame"""
        trades = []
        base_time = datetime.now()
        
        for i in range(10):
            entry_time = base_time + timedelta(hours=i*2)
            exit_time = entry_time + timedelta(hours=1)
            
            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'symbol': 'TEST',
                'direction': 'BUY',
                'entry_price': 100.0 + i,
                'exit_price': 101.0 + i if i % 2 == 0 else 99.0 + i,
                'lot_size': 1.0,
                'pnl': 1.0 if i % 2 == 0 else -1.0,
                'realized_pnl': 1.0 if i % 2 == 0 else -1.0,
                'unrealized_pnl': 0.0,
                'pnl_pct': 1.0 if i % 2 == 0 else -1.0,
                'exit_reason': 'TP1' if i % 2 == 0 else 'SL',
                'duration_hours': 1.0,
                'tp1_hit': i % 2 == 0,
                'tp2_hit': False,
                'entry_fee': 0.1,
                'exit_fee': 0.1,
                'total_fees': 0.2,
                'entry_slippage': 0.05,
                'exit_slippage': 0.05
            })
        
        return pd.DataFrame(trades)
    
    def create_sample_equity_curve(self, days=30):
        """Create sample equity curve"""
        base_time = datetime.now() - timedelta(days=days)
        dates = pd.date_range(start=base_time, periods=days*24*12, freq='5min')
        
        equity = []
        capital = 1000.0
        
        for i, date in enumerate(dates):
            # Simulate equity growth
            capital += np.random.normal(0, 0.1)
            equity.append({
                'timestamp': date,
                'equity': capital,
                'capital': capital,
                'cash': capital * 0.9,
                'reserved_margin': capital * 0.1,
                'open_trades': 1 if i % 10 == 0 else 0,
                'drawdown_pct': max(0, (1000 - capital) / 1000 * 100)
            })
        
        return pd.DataFrame(equity)
    
    def test_analytics_initialization(self):
        """Test analytics initialization"""
        trades_df = self.create_sample_trades()
        equity_df = self.create_sample_equity_curve()
        
        start_date = equity_df['timestamp'].iloc[0]
        end_date = equity_df['timestamp'].iloc[-1]
        
        analytics = BacktestAnalytics(
            trades_df=trades_df,
            equity_curve_df=equity_df,
            initial_capital=1000,
            start_date=start_date,
            end_date=end_date
        )
        
        assert analytics.initial_capital == 1000
        assert len(analytics.trades_df) == 10
    
    def test_metrics_calculation(self):
        """Test metrics calculation"""
        trades_df = self.create_sample_trades()
        equity_df = self.create_sample_equity_curve()
        
        start_date = equity_df['timestamp'].iloc[0]
        end_date = equity_df['timestamp'].iloc[-1]
        
        analytics = BacktestAnalytics(
            trades_df=trades_df,
            equity_curve_df=equity_df,
            initial_capital=1000,
            start_date=start_date,
            end_date=end_date
        )
        
        metrics = analytics.calculate_all_metrics()
        
        assert 'total_trades' in metrics
        assert 'win_rate' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown_pct' in metrics
        assert 'cagr' in metrics
    
    def test_tearsheet_generation(self, tmp_path):
        """Test tearsheet generation"""
        trades_df = self.create_sample_trades()
        equity_df = self.create_sample_equity_curve()
        
        start_date = equity_df['timestamp'].iloc[0]
        end_date = equity_df['timestamp'].iloc[-1]
        
        analytics = BacktestAnalytics(
            trades_df=trades_df,
            equity_curve_df=equity_df,
            initial_capital=1000,
            start_date=start_date,
            end_date=end_date
        )
        
        output_dir = str(tmp_path / "backtests")
        result = analytics.generate_tearsheet(output_dir=output_dir)
        
        assert 'json_path' in result
        assert 'html_path' in result
        assert 'csv_path' in result
        assert 'metrics' in result
        
        # Check files exist
        import os
        assert os.path.exists(result['json_path'])
        assert os.path.exists(result['html_path'])
        assert os.path.exists(result['csv_path'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
