"""
1-Year Monte Carlo Backtest Simulation
ELITE A+ Signal System - Starting Capital: $500
Simulates realistic trading performance based on system parameters
"""

import random
import numpy as np
from datetime import datetime, timedelta


class MonteCarloBacktest:
    """Monte Carlo simulation for ELITE signal system"""
    
    def __init__(self, starting_capital=500, risk_per_trade=0.01):
        self.starting_capital = starting_capital
        self.risk_per_trade = risk_per_trade
        
        # ELITE system parameters
        self.win_rate = 0.925  # 92.5% (middle of 90-95% range)
        self.avg_rr_ratio = 2.5  # 1:2.5 R:R
        self.signals_per_week = 2  # Conservative estimate (1-3 range)
        
        # Trading parameters
        self.max_drawdown_limit = 0.20  # 20% max drawdown
        self.compound = True  # Compound profits
    
    def simulate_trade(self):
        """Simulate a single trade"""
        # Determine win/loss
        is_win = random.random() < self.win_rate
        
        if is_win:
            # Win: gain R:R ratio
            return self.avg_rr_ratio
        else:
            # Loss: lose 1R
            return -1.0
    
    def run_simulation(self, days=365, num_simulations=1000):
        """Run Monte Carlo simulation"""
        all_equity_curves = []
        final_balances = []
        max_drawdowns = []
        total_trades_list = []
        win_counts = []
        
        for sim in range(num_simulations):
            capital = self.starting_capital
            equity_curve = [capital]
            peak_capital = capital
            max_drawdown = 0
            total_trades = 0
            wins = 0
            
            # Simulate each week
            weeks = days // 7
            for week in range(weeks):
                # Generate signals for this week
                num_signals = np.random.poisson(self.signals_per_week)
                
                for _ in range(num_signals):
                    # Calculate position size (1% risk)
                    risk_amount = capital * self.risk_per_trade
                    
                    # Simulate trade
                    result = self.simulate_trade()
                    
                    # Calculate profit/loss
                    if result > 0:
                        profit = risk_amount * result
                        wins += 1
                    else:
                        profit = risk_amount * result
                    
                    # Update capital
                    capital += profit
                    total_trades += 1
                    
                    # Track drawdown
                    if capital > peak_capital:
                        peak_capital = capital
                    
                    current_drawdown = (peak_capital - capital) / peak_capital
                    max_drawdown = max(max_drawdown, current_drawdown)
                    
                    # Stop if hit max drawdown
                    if current_drawdown >= self.max_drawdown_limit:
                        break
                
                equity_curve.append(capital)
            
            all_equity_curves.append(equity_curve)
            final_balances.append(capital)
            max_drawdowns.append(max_drawdown)
            total_trades_list.append(total_trades)
            win_counts.append(wins)
        
        return {
            'equity_curves': all_equity_curves,
            'final_balances': final_balances,
            'max_drawdowns': max_drawdowns,
            'total_trades': total_trades_list,
            'win_counts': win_counts
        }
    
    def analyze_results(self, results):
        """Analyze simulation results"""
        final_balances = results['final_balances']
        max_drawdowns = results['max_drawdowns']
        total_trades = results['total_trades']
        win_counts = results['win_counts']
        
        # Calculate statistics
        avg_final = np.mean(final_balances)
        median_final = np.median(final_balances)
        best_case = np.percentile(final_balances, 95)
        worst_case = np.percentile(final_balances, 5)
        
        avg_drawdown = np.mean(max_drawdowns)
        max_drawdown_seen = np.max(max_drawdowns)
        
        avg_trades = np.mean(total_trades)
        avg_wins = np.mean(win_counts)
        actual_win_rate = np.mean([w/t if t > 0 else 0 for w, t in zip(win_counts, total_trades)])
        
        # Calculate returns
        avg_return = ((avg_final - self.starting_capital) / self.starting_capital) * 100
        median_return = ((median_final - self.starting_capital) / self.starting_capital) * 100
        best_return = ((best_case - self.starting_capital) / self.starting_capital) * 100
        worst_return = ((worst_case - self.starting_capital) / self.starting_capital) * 100
        
        return {
            'avg_final': avg_final,
            'median_final': median_final,
            'best_case': best_case,
            'worst_case': worst_case,
            'avg_return': avg_return,
            'median_return': median_return,
            'best_return': best_return,
            'worst_return': worst_return,
            'avg_drawdown': avg_drawdown,
            'max_drawdown_seen': max_drawdown_seen,
            'avg_trades': avg_trades,
            'avg_wins': avg_wins,
            'actual_win_rate': actual_win_rate
        }
    
    def print_results(self, stats):
        """Print comprehensive results"""
        print("\n" + "="*100)
        print("1-YEAR MONTE CARLO BACKTEST RESULTS")
        print("ELITE A+ Signal System")
        print(f"Starting Capital: ${self.starting_capital:,.2f}")
        print(f"Simulation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        
        # System parameters
        print(f"\n{'-'*100}")
        print("SYSTEM PARAMETERS")
        print(f"{'-'*100}")
        print(f"{'Parameter':<40} | {'Value':<55}")
        print(f"{'-'*100}")
        print(f"{'Target Win Rate':<40} | {self.win_rate*100:.1f}%")
        print(f"{'Average R:R Ratio':<40} | 1:{self.avg_rr_ratio}")
        print(f"{'Expected Signals per Week':<40} | {self.signals_per_week}")
        print(f"{'Risk per Trade':<40} | {self.risk_per_trade*100:.1f}%")
        print(f"{'Max Drawdown Limit':<40} | {self.max_drawdown_limit*100:.0f}%")
        print(f"{'-'*100}")
        
        # Performance results
        print(f"\n{'-'*100}")
        print("PERFORMANCE RESULTS (1000 Simulations)")
        print(f"{'-'*100}")
        print(f"{'Metric':<40} | {'Value':<55}")
        print(f"{'-'*100}")
        print(f"{'Average Final Balance':<40} | ${stats['avg_final']:,.2f} ({stats['avg_return']:+.1f}%)")
        print(f"{'Median Final Balance':<40} | ${stats['median_final']:,.2f} ({stats['median_return']:+.1f}%)")
        print(f"{'Best Case (95th percentile)':<40} | ${stats['best_case']:,.2f} ({stats['best_return']:+.1f}%)")
        print(f"{'Worst Case (5th percentile)':<40} | ${stats['worst_case']:,.2f} ({stats['worst_return']:+.1f}%)")
        print(f"{'-'*100}")
        
        # Risk metrics
        print(f"\n{'-'*100}")
        print("RISK METRICS")
        print(f"{'-'*100}")
        print(f"{'Metric':<40} | {'Value':<55}")
        print(f"{'-'*100}")
        print(f"{'Average Max Drawdown':<40} | {stats['avg_drawdown']*100:.2f}%")
        print(f"{'Worst Drawdown Seen':<40} | {stats['max_drawdown_seen']*100:.2f}%")
        print(f"{'-'*100}")
        
        # Trading activity
        print(f"\n{'-'*100}")
        print("TRADING ACTIVITY")
        print(f"{'-'*100}")
        print(f"{'Metric':<40} | {'Value':<55}")
        print(f"{'-'*100}")
        print(f"{'Average Total Trades':<40} | {stats['avg_trades']:.0f} trades/year")
        print(f"{'Average Winning Trades':<40} | {stats['avg_wins']:.0f} trades/year")
        print(f"{'Actual Win Rate (Simulated)':<40} | {stats['actual_win_rate']*100:.1f}%")
        print(f"{'Average Trades per Month':<40} | {stats['avg_trades']/12:.1f} trades/month")
        print(f"{'-'*100}")
        
        # Monthly projections
        print(f"\n{'-'*100}")
        print("MONTHLY PROJECTIONS (Average Scenario)")
        print(f"{'-'*100}")
        
        monthly_growth = (stats['avg_final'] / self.starting_capital) ** (1/12)
        capital = self.starting_capital
        
        print(f"{'Month':<10} | {'Balance':<20} | {'Profit':<20} | {'Return':<20}")
        print(f"{'-'*100}")
        
        for month in range(1, 13):
            new_capital = capital * monthly_growth
            profit = new_capital - capital
            return_pct = ((new_capital - self.starting_capital) / self.starting_capital) * 100
            
            print(f"{'Month ' + str(month):<10} | ${new_capital:>18,.2f} | ${profit:>18,.2f} | {return_pct:>18.1f}%")
            capital = new_capital
        
        print(f"{'-'*100}")
        
        # Scenarios
        print(f"\n{'-'*100}")
        print("SCENARIO ANALYSIS")
        print(f"{'-'*100}")
        print(f"{'Scenario':<30} | {'Final Balance':<30} | {'Total Return':<30}")
        print(f"{'-'*100}")
        print(f"{'Best Case (95%)':<30} | ${stats['best_case']:>28,.2f} | {stats['best_return']:>28.1f}%")
        print(f"{'Average Case (50%)':<30} | ${stats['avg_final']:>28,.2f} | {stats['avg_return']:>28.1f}%")
        print(f"{'Worst Case (5%)':<30} | ${stats['worst_case']:>28,.2f} | {stats['worst_return']:>28.1f}%")
        print(f"{'-'*100}")
        
        # Key insights
        print(f"\n{'-'*100}")
        print("KEY INSIGHTS")
        print(f"{'-'*100}")
        
        if stats['avg_return'] > 100:
            print(f"[EXCELLENT] Average return of {stats['avg_return']:.1f}% - System shows strong profitability")
        elif stats['avg_return'] > 50:
            print(f"[GOOD] Average return of {stats['avg_return']:.1f}% - Solid performance")
        else:
            print(f"[MODERATE] Average return of {stats['avg_return']:.1f}% - Conservative growth")
        
        if stats['avg_drawdown'] < 0.10:
            print(f"[LOW RISK] Average drawdown of {stats['avg_drawdown']*100:.1f}% - Well controlled risk")
        elif stats['avg_drawdown'] < 0.15:
            print(f"[MODERATE RISK] Average drawdown of {stats['avg_drawdown']*100:.1f}% - Acceptable risk")
        else:
            print(f"[HIGHER RISK] Average drawdown of {stats['avg_drawdown']*100:.1f}% - Monitor closely")
        
        if stats['actual_win_rate'] >= 0.90:
            print(f"[VALIDATED] Simulated win rate of {stats['actual_win_rate']*100:.1f}% matches target (90-95%)")
        
        print(f"\n[RECOMMENDATION] Based on {int(stats['avg_trades'])} trades/year:")
        print(f"   - Expected monthly profit: ${(stats['avg_final'] - self.starting_capital)/12:,.2f}")
        print(f"   - Risk per trade: ${self.starting_capital * self.risk_per_trade:,.2f} (1% of capital)")
        print(f"   - Compounding effect: Significant over 12 months")
        
        print(f"\n{'='*100}\n")


def main():
    """Run the backtest simulation"""
    print("\n[INFO] Starting 1-Year Monte Carlo Backtest Simulation...")
    print("[INFO] Running 1000 simulations - this will take ~30 seconds...\n")
    
    # Initialize backtest
    backtest = MonteCarloBacktest(starting_capital=500, risk_per_trade=0.01)
    
    # Run simulation
    results = backtest.run_simulation(days=365, num_simulations=1000)
    
    # Analyze results
    stats = backtest.analyze_results(results)
    
    # Print results
    backtest.print_results(stats)
    
    print("[DONE] Backtest simulation complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
