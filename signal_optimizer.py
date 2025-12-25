"""
Signal Optimizer
Optimize trading strategy parameters using grid search and walk-forward analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from itertools import product
from datetime import datetime

from historical_data import HistoricalDataManager
from backtest_engine import BacktestEngine
from performance_metrics import PerformanceMetrics

class SignalOptimizer:
    """Optimize trading signal parameters"""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 500):
        self.data = data
        self.initial_capital = initial_capital
        self.best_params = None
        self.optimization_results = []
    
    def grid_search(self, param_grid: Dict, strategy_func) -> pd.DataFrame:
        """
        Perform grid search over parameter space
        
        Args:
            param_grid: Dictionary of parameters to test
                Example: {
                    'signal_threshold': [0.2, 0.3, 0.4],
                    'tp_multiplier': [1.5, 2.0, 2.5],
                    'sl_multiplier': [1.0, 1.5, 2.0]
                }
            strategy_func: Function that generates signals given parameters
        
        Returns:
            DataFrame with results for each parameter combination
        """
        print("=" * 70)
        print("🔍 GRID SEARCH OPTIMIZATION")
        print("=" * 70)
        print(f"Testing {np.prod([len(v) for v in param_grid.values()])} combinations...")
        print()
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        results = []
        
        for i, combo in enumerate(combinations, 1):
            params = dict(zip(param_names, combo))
            
            print(f"Testing {i}/{len(combinations)}: {params}")
            
            # Run backtest with these parameters
            metrics = self._run_backtest_with_params(params, strategy_func)
            
            if metrics:
                result = {**params, **metrics}
                results.append(result)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Sort by Sharpe ratio (or other metric)
        if len(results_df) > 0:
            results_df = results_df.sort_values('sharpe_ratio', ascending=False)
            
            print("\n" + "=" * 70)
            print("✅ OPTIMIZATION COMPLETE")
            print("=" * 70)
            print("\nTop 5 Parameter Sets:")
            print(results_df.head().to_string())
            
            # Store best params
            self.best_params = results_df.iloc[0][param_names].to_dict()
            print(f"\n🏆 Best Parameters: {self.best_params}")
        
        self.optimization_results = results_df
        return results_df
    
    def _run_backtest_with_params(self, params: Dict, strategy_func) -> Dict:
        """Run backtest with specific parameters"""
        try:
            # Create strategy function with these params
            def parameterized_strategy(data):
                return strategy_func(data, **params)
            
            # Run backtest
            engine = BacktestEngine(
                initial_capital=self.initial_capital,
                risk_per_trade=0.01
            )
            
            engine.run_backtest(self.data, parameterized_strategy, verbose=False)
            
            # Calculate metrics
            trades_df = engine.get_trades_df()
            equity_df = engine.get_equity_curve_df()
            
            if len(trades_df) == 0:
                return None
            
            metrics_calc = PerformanceMetrics(trades_df, equity_df, self.initial_capital)
            metrics = metrics_calc.calculate_all_metrics()
            
            return {
                'total_return_pct': metrics['total_return_pct'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown_pct': metrics['max_drawdown_pct'],
                'win_rate': metrics['win_rate'],
                'profit_factor': metrics['profit_factor'],
                'total_trades': metrics['total_trades']
            }
            
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    def walk_forward_analysis(self, param_grid: Dict, strategy_func,
                             train_days: int = 180, test_days: int = 30) -> pd.DataFrame:
        """
        Walk-forward optimization to avoid overfitting
        
        Args:
            param_grid: Parameters to optimize
            strategy_func: Strategy function
            train_days: Days for training/optimization
            test_days: Days for testing
        
        Returns:
            DataFrame with walk-forward results
        """
        print("=" * 70)
        print("🚶 WALK-FORWARD ANALYSIS")
        print("=" * 70)
        print(f"Train Period: {train_days} days")
        print(f"Test Period: {test_days} days")
        print()
        
        results = []
        
        # Split data into windows
        total_days = len(self.data)
        window_size = train_days + test_days
        
        for start_idx in range(0, total_days - window_size, test_days):
            train_end = start_idx + train_days
            test_end = train_end + test_days
            
            if test_end > total_days:
                break
            
            train_data = self.data.iloc[start_idx:train_end]
            test_data = self.data.iloc[train_end:test_end]
            
            print(f"\nWindow: {train_data.index[0]} to {test_data.index[-1]}")
            print(f"  Train: {len(train_data)} candles")
            print(f"  Test: {len(test_data)} candles")
            
            # Optimize on training data
            optimizer = SignalOptimizer(train_data, self.initial_capital)
            train_results = optimizer.grid_search(param_grid, strategy_func)
            
            if len(train_results) == 0:
                continue
            
            # Get best params from training
            best_params = optimizer.best_params
            
            # Test on out-of-sample data
            test_metrics = self._run_backtest_with_params(best_params, strategy_func)
            
            if test_metrics:
                results.append({
                    'window_start': train_data.index[0],
                    'window_end': test_data.index[-1],
                    **best_params,
                    **{f'test_{k}': v for k, v in test_metrics.items()}
                })
        
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            print("\n" + "=" * 70)
            print("✅ WALK-FORWARD ANALYSIS COMPLETE")
            print("=" * 70)
            print("\nAverage Test Performance:")
            print(f"  Return: {results_df['test_total_return_pct'].mean():.2f}%")
            print(f"  Sharpe: {results_df['test_sharpe_ratio'].mean():.2f}")
            print(f"  Win Rate: {results_df['test_win_rate'].mean():.2f}%")
        
        return results_df
    
    def optimize_signal_thresholds(self) -> Dict:
        """Optimize BUY/SELL signal thresholds"""
        param_grid = {
            'buy_threshold': [0.2, 0.25, 0.3, 0.35, 0.4],
            'sell_threshold': [-0.2, -0.25, -0.3, -0.35, -0.4],
            'min_confidence': [60, 65, 70, 75]
        }
        
        def threshold_strategy(data, buy_threshold, sell_threshold, min_confidence):
            # Simplified strategy for demonstration
            if len(data) < 20:
                return {'direction': 'HOLD'}
            
            current_price = data['close'].iloc[-1]
            sma_short = data['close'].iloc[-10:].mean()
            sma_long = data['close'].iloc[-20:].mean()
            
            signal_strength = (sma_short - sma_long) / sma_long
            
            volatility = data['close'].pct_change().std()
            stop_distance = current_price * volatility * 2
            
            if signal_strength > buy_threshold:
                return {
                    'direction': 'BUY',
                    'entry_price': current_price,
                    'stop_loss': current_price - stop_distance,
                    'take_profit_1': current_price + stop_distance * 1.2,
                    'take_profit_2': current_price + stop_distance * 2.5,
                    'confidence': min(95, 50 + abs(signal_strength) * 100)
                }
            elif signal_strength < sell_threshold:
                return {
                    'direction': 'SELL',
                    'entry_price': current_price,
                    'stop_loss': current_price + stop_distance,
                    'take_profit_1': current_price - stop_distance * 1.2,
                    'take_profit_2': current_price - stop_distance * 2.5,
                    'confidence': min(95, 50 + abs(signal_strength) * 100)
                }
            else:
                return {'direction': 'HOLD'}
        
        results = self.grid_search(param_grid, threshold_strategy)
        return self.best_params


class SignalStrengthScorer:
    """Calculate signal strength score from multiple factors"""
    
    def __init__(self):
        self.weights = {
            'trend': 0.25,
            'momentum': 0.20,
            'volatility': 0.15,
            'volume': 0.15,
            'sentiment': 0.15,
            'confluence': 0.10
        }
    
    def calculate_score(self, market_data: Dict, signal: Dict) -> float:
        """
        Calculate overall signal strength (0-100)
        
        Args:
            market_data: Current market data
            signal: Trading signal
        
        Returns:
            Signal strength score (0-100)
        """
        scores = {}
        
        # 1. Trend Score (0-100)
        # Higher if aligned with trend
        scores['trend'] = self._calculate_trend_score(market_data, signal)
        
        # 2. Momentum Score (0-100)
        scores['momentum'] = self._calculate_momentum_score(market_data)
        
        # 3. Volatility Score (0-100)
        # Optimal volatility range
        scores['volatility'] = self._calculate_volatility_score(market_data)
        
        # 4. Volume Score (0-100)
        scores['volume'] = self._calculate_volume_score(market_data)
        
        # 5. Sentiment Score (0-100)
        scores['sentiment'] = market_data.get('market_sentiment', 0.5) * 100
        
        # 6. Confluence Score (0-100)
        # Multiple indicators agreeing
        scores['confluence'] = self._calculate_confluence_score(scores)
        
        # Weighted average
        total_score = sum(scores[k] * self.weights[k] for k in scores.keys())
        
        return round(total_score, 1)
    
    def _calculate_trend_score(self, market_data: Dict, signal: Dict) -> float:
        """Score based on trend alignment"""
        # Simplified - would use actual trend indicators
        direction = signal.get('direction', 'HOLD')
        
        if direction == 'HOLD':
            return 50
        
        # Assume bullish market if price > some threshold
        # In real implementation, use moving averages
        return 75 if direction == 'BUY' else 60
    
    def _calculate_momentum_score(self, market_data: Dict) -> float:
        """Score based on momentum"""
        # Would use RSI, MACD, etc.
        return 70  # Placeholder
    
    def _calculate_volatility_score(self, market_data: Dict) -> float:
        """Score based on volatility (optimal range)"""
        vol = market_data.get('btc_volatility', 0.03)
        
        # Optimal range: 3-5%
        if 0.03 <= vol <= 0.05:
            return 100
        elif 0.02 <= vol <= 0.06:
            return 75
        elif vol > 0.08:
            return 30  # Too volatile
        else:
            return 50
    
    def _calculate_volume_score(self, market_data: Dict) -> float:
        """Score based on volume"""
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        if volume_ratio > 1.5:
            return 100
        elif volume_ratio > 1.2:
            return 80
        elif volume_ratio > 1.0:
            return 60
        else:
            return 40
    
    def _calculate_confluence_score(self, scores: Dict) -> float:
        """Score based on how many indicators agree"""
        # Count how many scores are > 70
        high_scores = sum(1 for s in scores.values() if s > 70)
        total_scores = len(scores) - 1  # Exclude confluence itself
        
        return (high_scores / total_scores) * 100 if total_scores > 0 else 50


# Test the optimizer
if __name__ == "__main__":
    print("Signal Optimizer ready!")
    print("\nTo use:")
    print("1. Load historical data")
    print("2. Define parameter grid")
    print("3. Run grid_search() or walk_forward_analysis()")
    print("\nExample:")
    print("  optimizer = SignalOptimizer(data)")
    print("  results = optimizer.optimize_signal_thresholds()")
