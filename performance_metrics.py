"""
Performance Metrics Calculator
Calculates comprehensive trading performance statistics
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class PerformanceMetrics:
    """Calculate trading performance metrics"""
    
    def __init__(self, trades_df: pd.DataFrame, equity_curve_df: pd.DataFrame, 
                 initial_capital: float):
        self.trades_df = trades_df
        self.equity_curve_df = equity_curve_df
        self.initial_capital = initial_capital
        
        if len(trades_df) > 0:
            self.final_capital = equity_curve_df['equity'].iloc[-1]
        else:
            self.final_capital = initial_capital
    
    def calculate_all_metrics(self) -> Dict:
        """Calculate all performance metrics"""
        if len(self.trades_df) == 0:
            return self._empty_metrics()
        
        metrics = {}
        
        # Basic metrics
        metrics.update(self._calculate_basic_metrics())
        
        # Risk-adjusted metrics
        metrics.update(self._calculate_risk_metrics())
        
        # Trade analysis
        metrics.update(self._calculate_trade_metrics())
        
        return metrics
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics when no trades"""
        return {
            'total_trades': 0,
            'total_return_pct': 0,
            'total_pnl': 0,
            'message': 'No trades executed'
        }
    
    def _calculate_basic_metrics(self) -> Dict:
        """Calculate basic performance metrics"""
        total_trades = len(self.trades_df)
        winning_trades = self.trades_df[self.trades_df['pnl'] > 0]
        losing_trades = self.trades_df[self.trades_df['pnl'] < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = self.trades_df['pnl'].sum()
        total_return = (self.final_capital - self.initial_capital) / self.initial_capital * 100
        
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'best_trade': self.trades_df['pnl'].max(),
            'worst_trade': self.trades_df['pnl'].min()
        }
    
    def _calculate_risk_metrics(self) -> Dict:
        """Calculate risk-adjusted metrics"""
        equity = self.equity_curve_df['equity'].values
        returns = pd.Series(equity).pct_change().dropna()
        
        # Sharpe Ratio (annualized, assuming 365 days)
        if len(returns) > 0 and returns.std() != 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(365 * 24 * 12)  # 5-min periods
        else:
            sharpe = 0
        
        # Maximum Drawdown
        peak = pd.Series(equity).expanding().max()
        drawdown = (pd.Series(equity) - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() != 0:
            sortino = (returns.mean() / downside_returns.std()) * np.sqrt(365 * 24 * 12)
        else:
            sortino = 0
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_pct': max_drawdown,
            'volatility': returns.std() * 100 if len(returns) > 0 else 0
        }
    
    def _calculate_trade_metrics(self) -> Dict:
        """Calculate trade-specific metrics"""
        if len(self.trades_df) == 0:
            return {}
        
        # Average trade duration
        avg_duration = self.trades_df['duration_hours'].mean()
        
        # TP hit rates
        tp1_hit_rate = (self.trades_df['tp1_hit'].sum() / len(self.trades_df)) * 100
        tp2_hit_rate = (self.trades_df['tp2_hit'].sum() / len(self.trades_df)) * 100
        
        # Exit reason breakdown
        exit_reasons = self.trades_df['exit_reason'].value_counts().to_dict()
        
        # Consecutive wins/losses
        pnl_signs = (self.trades_df['pnl'] > 0).astype(int)
        consecutive_wins = self._max_consecutive(pnl_signs, 1)
        consecutive_losses = self._max_consecutive(pnl_signs, 0)
        
        return {
            'avg_trade_duration_hours': avg_duration,
            'tp1_hit_rate': tp1_hit_rate,
            'tp2_hit_rate': tp2_hit_rate,
            'exit_reasons': exit_reasons,
            'max_consecutive_wins': consecutive_wins,
            'max_consecutive_losses': consecutive_losses
        }
    
    def _max_consecutive(self, series: pd.Series, value: int) -> int:
        """Calculate maximum consecutive occurrences of a value"""
        max_count = 0
        current_count = 0
        
        for v in series:
            if v == value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def print_report(self):
        """Print comprehensive performance report"""
        metrics = self.calculate_all_metrics()
        
        if metrics.get('total_trades', 0) == 0:
            print("=" * 70)
            print("No trades executed in backtest")
            print("=" * 70)
            return
        
        print("=" * 70)
        print("📊 PERFORMANCE REPORT")
        print("=" * 70)
        print()
        print("BASIC METRICS:")
        print("-" * 70)
        print(f"Total Trades:           {metrics['total_trades']}")
        print(f"Winning Trades:         {metrics['winning_trades']}")
        print(f"Losing Trades:          {metrics['losing_trades']}")
        print(f"Win Rate:               {metrics['win_rate']:.1f}%")
        print()
        print(f"Initial Capital:        ${self.initial_capital:,.2f}")
        print(f"Final Capital:          ${self.final_capital:,.2f}")
        print(f"Total P&L:              ${metrics['total_pnl']:+,.2f}")
        print(f"Total Return:           {metrics['total_return_pct']:+.2f}%")
        print()
        print("TRADE ANALYSIS:")
        print("-" * 70)
        print(f"Average Win:            ${metrics['avg_win']:,.2f}")
        print(f"Average Loss:           ${metrics['avg_loss']:,.2f}")
        print(f"Profit Factor:          {metrics['profit_factor']:.2f}")
        print(f"Best Trade:             ${metrics['best_trade']:+,.2f}")
        print(f"Worst Trade:            ${metrics['worst_trade']:+,.2f}")
        print(f"Avg Duration:           {metrics['avg_trade_duration_hours']:.1f} hours")
        print()
        print("TAKE PROFIT ANALYSIS:")
        print("-" * 70)
        print(f"TP1 Hit Rate:           {metrics['tp1_hit_rate']:.1f}%")
        print(f"TP2 Hit Rate:           {metrics['tp2_hit_rate']:.1f}%")
        print()
        print("EXIT REASONS:")
        print("-" * 70)
        for reason, count in metrics['exit_reasons'].items():
            pct = (count / metrics['total_trades']) * 100
            print(f"{reason:20s} {count:3d} ({pct:.1f}%)")
        print()
        print("RISK METRICS:")
        print("-" * 70)
        print(f"Sharpe Ratio:           {metrics['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:          {metrics['sortino_ratio']:.2f}")
        print(f"Max Drawdown:           {metrics['max_drawdown_pct']:.2f}%")
        print(f"Volatility:             {metrics['volatility']:.2f}%")
        print()
        print("STREAKS:")
        print("-" * 70)
        print(f"Max Consecutive Wins:   {metrics['max_consecutive_wins']}")
        print(f"Max Consecutive Losses: {metrics['max_consecutive_losses']}")
        print("=" * 70)


if __name__ == "__main__":
    print("Performance metrics calculator ready!")
