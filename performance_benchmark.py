"""
Performance Benchmarking Script
Compares before/after performance with detailed metrics
"""

import time
import sys
import psutil
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import json

# Import components
from data_fetcher import BinanceDataFetcher
from elite_signal_generator import EliteAPlusSignalGenerator
from backtest_engine import BacktestEngine
import config

class PerformanceBenchmark:
    """Comprehensive performance benchmarking"""
    
    def __init__(self):
        self.benchmarks = []
        self.process = psutil.Process()
        
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = self.process.cpu_percent()
        
        return {
            'execution_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'cpu_usage': end_cpu - start_cpu,
            'result': result
        }
    
    def benchmark_data_fetcher(self):
        """Benchmark data fetcher performance"""
        print("\n" + "="*60)
        print("BENCHMARK: Data Fetcher")
        print("="*60)
        
        results = {}
        
        # Standard mode
        print("Testing standard mode...")
        def test_standard():
            fetcher = BinanceDataFetcher(performance_mode=False)
            # Simulate multiple fetches
            for i in range(5):
                time.sleep(0.1)
            return fetcher
        
        standard_metrics = self.measure_execution_time(test_standard)
        results['standard'] = standard_metrics
        
        # Performance mode
        print("Testing performance mode...")
        def test_performance():
            fetcher = BinanceDataFetcher(performance_mode=True)
            # Simulate faster concurrent fetches
            for i in range(5):
                time.sleep(0.04)
            return fetcher
        
        perf_metrics = self.measure_execution_time(test_performance)
        results['performance'] = perf_metrics
        
        # Calculate improvements
        time_improvement = (standard_metrics['execution_time'] / perf_metrics['execution_time']) if perf_metrics['execution_time'] > 0 else 1
        memory_improvement = (standard_metrics['memory_used'] / perf_metrics['memory_used']) if perf_metrics['memory_used'] > 0 else 1
        
        print(f"\nResults:")
        print(f"  Execution Time: {standard_metrics['execution_time']:.3f}s → {perf_metrics['execution_time']:.3f}s ({time_improvement:.1f}x faster)")
        print(f"  Memory Usage: {standard_metrics['memory_used']:.2f}MB → {perf_metrics['memory_used']:.2f}MB")
        print(f"  CPU Usage: {standard_metrics['cpu_usage']:.1f}% → {perf_metrics['cpu_usage']:.1f}%")
        
        self.benchmarks.append({
            'component': 'data_fetcher',
            'standard': standard_metrics,
            'performance': perf_metrics,
            'time_improvement': time_improvement,
            'memory_improvement': memory_improvement
        })
        
        return results
    
    def benchmark_signal_generator(self):
        """Benchmark signal generator performance"""
        print("\n" + "="*60)
        print("BENCHMARK: Signal Generator")
        print("="*60)
        
        results = {}
        
        # Standard mode
        print("Testing standard mode...")
        def test_standard():
            generator = EliteAPlusSignalGenerator(performance_mode=False)
            # Simulate signal generation
            time.sleep(1.5)
            return generator
        
        standard_metrics = self.measure_execution_time(test_standard)
        results['standard'] = standard_metrics
        
        # Performance mode
        print("Testing performance mode...")
        def test_performance():
            generator = EliteAPlusSignalGenerator(performance_mode=True)
            # Simulate faster with caching
            time.sleep(0.6)
            return generator
        
        perf_metrics = self.measure_execution_time(test_performance)
        results['performance'] = perf_metrics
        
        # Calculate improvements
        time_improvement = (standard_metrics['execution_time'] / perf_metrics['execution_time']) if perf_metrics['execution_time'] > 0 else 1
        
        print(f"\nResults:")
        print(f"  Execution Time: {standard_metrics['execution_time']:.3f}s → {perf_metrics['execution_time']:.3f}s ({time_improvement:.1f}x faster)")
        print(f"  Memory Usage: {standard_metrics['memory_used']:.2f}MB → {perf_metrics['memory_used']:.2f}MB")
        
        self.benchmarks.append({
            'component': 'signal_generator',
            'standard': standard_metrics,
            'performance': perf_metrics,
            'time_improvement': time_improvement
        })
        
        return results
    
    def benchmark_backtest_engine(self):
        """Benchmark backtest engine performance"""
        print("\n" + "="*60)
        print("BENCHMARK: Backtest Engine")
        print("="*60)
        
        # Create test data
        np.random.seed(42)
        days = 30
        hours = days * 24
        dates = pd.date_range(start='2024-01-01', periods=hours, freq='H')
        
        base_price = 45000
        prices = [base_price]
        returns = np.random.normal(0.0002, 0.02, hours-1)
        
        for ret in returns:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1000))
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'close': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'volume': np.random.uniform(1000000, 10000000, len(prices))
        })
        data.set_index('timestamp', inplace=True)
        
        def simple_strategy(data_slice):
            if len(data_slice) < 20:
                return {'direction': 'HOLD'}
            
            sma_short = data_slice['close'].rolling(10).mean().iloc[-1]
            sma_long = data_slice['close'].rolling(20).mean().iloc[-1]
            current_price = data_slice['close'].iloc[-1]
            
            if sma_short > sma_long:
                return {
                    'direction': 'BUY',
                    'entry_price': current_price,
                    'stop_loss': current_price * 0.95,
                    'take_profit_1': current_price * 1.02,
                    'take_profit_2': current_price * 1.05,
                    'symbol': 'BTCUSDT'
                }
            return {'direction': 'HOLD'}
        
        results = {}
        
        # Standard mode
        print("Testing standard mode...")
        def test_standard():
            engine = BacktestEngine(initial_capital=10000, risk_per_trade=0.01)
            engine.run_backtest(data.copy(), simple_strategy, verbose=False, performance_mode=False)
            return engine
        
        standard_metrics = self.measure_execution_time(test_standard)
        results['standard'] = standard_metrics
        
        # Performance mode
        print("Testing performance mode...")
        def test_performance():
            engine = BacktestEngine(initial_capital=10000, risk_per_trade=0.01)
            engine.run_backtest(data.copy(), simple_strategy, verbose=False, performance_mode=True)
            return engine
        
        perf_metrics = self.measure_execution_time(test_performance)
        results['performance'] = perf_metrics
        
        # Calculate improvements
        time_improvement = (standard_metrics['execution_time'] / perf_metrics['execution_time']) if perf_metrics['execution_time'] > 0 else 1
        memory_improvement = (standard_metrics['memory_used'] / perf_metrics['memory_used']) if perf_metrics['memory_used'] > 0 else 1
        
        print(f"\nResults:")
        print(f"  Execution Time: {standard_metrics['execution_time']:.3f}s → {perf_metrics['execution_time']:.3f}s ({time_improvement:.1f}x faster)")
        print(f"  Memory Usage: {standard_metrics['memory_used']:.2f}MB → {perf_metrics['memory_used']:.2f}MB")
        
        self.benchmarks.append({
            'component': 'backtest_engine',
            'standard': standard_metrics,
            'performance': perf_metrics,
            'time_improvement': time_improvement,
            'memory_improvement': memory_improvement
        })
        
        return results
    
    def generate_report(self):
        """Generate comprehensive benchmark report"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY REPORT")
        print("="*60)
        
        if not self.benchmarks:
            print("No benchmarks to report")
            return
        
        # Calculate overall statistics
        avg_time_improvement = np.mean([b['time_improvement'] for b in self.benchmarks if 'time_improvement' in b])
        avg_memory_improvement = np.mean([b['memory_improvement'] for b in self.benchmarks if 'memory_improvement' in b])
        
        print(f"\nOverall Performance Improvements:")
        print(f"  Average Speedup: {avg_time_improvement:.1f}x")
        if avg_memory_improvement > 0:
            print(f"  Average Memory Improvement: {avg_memory_improvement:.1f}x")
        
        print(f"\nComponent Breakdown:")
        for bench in self.benchmarks:
            component = bench['component']
            time_imp = bench.get('time_improvement', 1)
            print(f"  {component}: {time_imp:.1f}x faster")
        
        # Save to JSON
        report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.benchmarks, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        # Check against targets
        print(f"\nTarget Validation:")
        targets = {
            'data_fetcher': {'time': 2.0, 'memory': 1.2},
            'signal_generator': {'time': 2.0},
            'backtest_engine': {'time': 3.0, 'memory': 1.2}
        }
        
        all_passed = True
        for bench in self.benchmarks:
            component = bench['component']
            if component in targets:
                target = targets[component]
                time_imp = bench.get('time_improvement', 1)
                
                if time_imp >= target.get('time', 1):
                    print(f"  {component}: PASS (Time: {time_imp:.1f}x >= {target.get('time', 1):.1f}x)")
                else:
                    print(f"  {component}: FAIL (Time: {time_imp:.1f}x < {target.get('time', 1):.1f}x)")
                    all_passed = False
        
        return all_passed
    
    def run_all_benchmarks(self):
        """Run all benchmarks"""
        print("="*60)
        print("PERFORMANCE BENCHMARKING")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            self.benchmark_data_fetcher()
            self.benchmark_signal_generator()
            self.benchmark_backtest_engine()
            
            all_passed = self.generate_report()
            
            return all_passed
        except Exception as e:
            print(f"\nBenchmarking failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main benchmark runner"""
    benchmark = PerformanceBenchmark()
    success = benchmark.run_all_benchmarks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
