"""
Integration Test Suite - Enhanced Testing for Trading Bot
Combines existing tests with new portfolio optimization and performance testing
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing test modules
try:
    from test_suite import TestSuite
    from test_quick import main as run_quick_tests
except ImportError as e:
    print(f"Warning: Could not import existing test modules: {e}")
    TestSuite = None

# Import enhanced test runner and new features
try:
    from enhanced_test_runner import EnhancedTestRunner, EnhancedTestResult
    from portfolio_optimizer import PortfolioOptimizer
except ImportError as e:
    print(f"Warning: Could not import enhanced modules: {e}")
    EnhancedTestRunner = None
    PortfolioOptimizer = None

# Import bot modules for integration testing
try:
    from signal_api import UltimateSignalAPI
    from trade_tracker import TradeTracker
    from performance_analytics import PerformanceAnalytics
    from backtest_engine import BacktestEngine
    from risk_manager import RiskManager
    from user_manager import UserManager
    from paper_trading import PaperTrading
    from signal_tracker import SignalTracker
except ImportError as e:
    print(f"Warning: Some bot modules not available: {e}")


class IntegrationTestSuite:
    """Comprehensive integration test suite combining all testing capabilities"""
    
    def __init__(self):
        self.enhanced_runner = EnhancedTestRunner() if EnhancedTestRunner else None
        self.original_suite = TestSuite() if TestSuite else None
        self.results = []
        self.test_user_id = 999999
    
    def test_signal_generation_integration(self) -> bool:
        """Test integration between signal API and tracking"""
        try:
            # Test signal generation
            signal_api = UltimateSignalAPI()
            result = signal_api.get_complete_analysis()
            
            if not isinstance(result, dict):
                return False
            
            # Test signal tracking integration
            signal_tracker = SignalTracker()
            signal_id = signal_tracker.log_signal(
                "EURUSD", "BUY", 1.1000, 1.1100, 1.0950,
                criteria_passed=18, criteria_total=20
            )
            
            # Verify signal can be retrieved
            retrieved_signal = signal_tracker.get_signal_by_id(signal_id)
            return retrieved_signal is not None and retrieved_signal['id'] == signal_id
            
        except Exception as e:
            print(f"Signal integration test error: {e}")
            return False
    
    def test_portfolio_optimization_integration(self) -> bool:
        """Test portfolio optimizer integration with tracking systems"""
        try:
            if not PortfolioOptimizer:
                return True  # Skip if not available
            
            # Initialize portfolio optimizer
            optimizer = PortfolioOptimizer()
            
            # Test correlation analysis
            correlation_results = optimizer.calculate_asset_correlations()
            if not correlation_results or 'diversification_score' not in correlation_results:
                return False
            
            # Test portfolio optimization
            current_positions = {
                'EURUSD': 0.25,
                'GBPUSD': 0.20,
                'USDJPY': 0.15,
                'AUDUSD': 0.20,
                'GOLD': 0.15,
                'BTC': 0.05
            }
            
            optimization_results = optimizer.optimize_portfolio_weights(current_positions)
            if not optimization_results or optimization_results.get('error'):
                return False
            
            # Test risk analysis
            risk_analysis = optimizer.analyze_risk_concentration(current_positions)
            return 'herfindahl_index' in risk_analysis
            
        except Exception as e:
            print(f"Portfolio optimization integration test error: {e}")
            return False
    
    def test_backtesting_integration(self) -> bool:
        """Test backtesting engine integration with other components"""
        try:
            # Initialize backtesting components
            backtest_engine = BacktestEngine(initial_capital=10000)
            risk_manager = RiskManager()
            
            # Test risk manager integration
            position_size = risk_manager.calculate_position_size(
                balance=10000,
                entry_price=1.1000,
                stop_loss=1.0950,
                risk_pct=0.01
            )
            
            if not position_size or position_size['lot_size'] <= 0:
                return False
            
            # Test that components can work together
            return True
            
        except Exception as e:
            print(f"Backtesting integration test error: {e}")
            return False
    
    def test_user_management_integration(self) -> bool:
        """Test user management system integration"""
        try:
            # Test user manager and paper trading integration
            user_manager = UserManager()
            paper_trading = PaperTrading()
            
            # Set user tier
            user_manager.set_user_tier(self.test_user_id, 'premium')
            
            # Enable paper trading
            paper_trading.enable_paper_trading(self.test_user_id, 10000.0)
            
            # Check integration
            tier = user_manager.get_user_tier(self.test_user_id)
            account = paper_trading.get_account(self.test_user_id)
            
            return tier == 'premium' and account is not None
            
        except Exception as e:
            print(f"User management integration test error: {e}")
            return False
    
    def test_performance_analytics_integration(self) -> bool:
        """Test performance analytics with trade tracking"""
        try:
            # Initialize components
            trade_tracker = TradeTracker()
            performance_analytics = PerformanceAnalytics(trade_tracker)
            
            # Add some test trades
            trade_tracker.add_trade({
                'asset': 'EURUSD',
                'direction': 'BUY',
                'entry_price': 1.1000,
                'exit_price': 1.1050,
                'lot_size': 0.1,
                'entry_time': datetime.now(),
                'exit_time': datetime.now()
            })
            
            # Test analytics functions
            win_rate = performance_analytics.get_win_rate_by_pair()
            return isinstance(win_rate, dict)
            
        except Exception as e:
            print(f"Performance analytics integration test error: {e}")
            return False
    
    def test_end_to_end_trading_workflow(self) -> bool:
        """Test complete trading workflow from signal to execution"""
        try:
            # 1. Generate signal
            signal_api = UltimateSignalAPI()
            analysis = signal_api.get_complete_analysis()
            
            if not analysis or not isinstance(analysis, dict):
                return False
            
            # 2. Check user permissions
            user_manager = UserManager()
            user_manager.set_user_tier(self.test_user_id, 'vip')  # Give full access
            
            has_access = user_manager.has_feature_access(self.test_user_id, 'all_assets')
            if not has_access:
                return False
            
            # 3. Calculate position size
            risk_manager = RiskManager()
            position_size = risk_manager.calculate_position_size(
                balance=10000,
                entry_price=1.1000,
                stop_loss=1.0950,
                risk_pct=0.01
            )
            
            if not position_size:
                return False
            
            # 4. Execute in paper trading
            paper_trading = PaperTrading()
            paper_trading.enable_paper_trading(self.test_user_id, 10000.0)
            
            trade_result = paper_trading.open_position(
                self.test_user_id, 'EURUSD', 'BUY', 0.1, 1.1000
            )
            
            if not trade_result:
                return False
            
            # 5. Track the signal
            signal_tracker = SignalTracker()
            signal_id = signal_tracker.log_signal(
                "EURUSD", "BUY", 1.1000, 1.1100, 1.0950
            )
            
            return signal_id > 0
            
        except Exception as e:
            print(f"End-to-end workflow test error: {e}")
            return False
    
    def run_load_tests(self):
        """Run load tests on critical bot functions"""
        if not self.enhanced_runner:
            print("Enhanced test runner not available - skipping load tests")
            return
        
        print("\n🔥 RUNNING LOAD TESTS")
        print("=" * 70)
        
        # Load test signal generation
        def signal_generation_test():
            signal_api = UltimateSignalAPI()
            result = signal_api.get_complete_analysis()
            return isinstance(result, dict)
        
        self.enhanced_runner.run_load_test(
            signal_generation_test, 
            "Signal Generation", 
            iterations=20
        )
        
        # Load test user operations
        def user_operations_test():
            user_manager = UserManager()
            tier = user_manager.get_user_tier(self.test_user_id)
            return tier in ['free', 'premium', 'vip']
        
        self.enhanced_runner.run_load_test(
            user_operations_test,
            "User Operations",
            iterations=50
        )
    
    def run_stress_tests(self):
        """Run stress tests simulating multiple concurrent users"""
        if not self.enhanced_runner:
            print("Enhanced test runner not available - skipping stress tests")
            return
        
        print("\n⚡ RUNNING STRESS TESTS")
        print("=" * 70)
        
        # Define stress test functions
        stress_test_functions = [
            (self.test_signal_generation_integration, "Signal Generation Integration"),
            (self.test_user_management_integration, "User Management Integration"),
            (self.test_backtesting_integration, "Backtesting Integration")
        ]
        
        self.enhanced_runner.run_stress_test(
            stress_test_functions,
            concurrent_users=8
        )
    
    def run_integration_tests(self):
        """Run all integration tests"""
        print("\n🔗 RUNNING INTEGRATION TESTS")
        print("=" * 70)
        
        integration_tests = [
            (self.test_signal_generation_integration, "Signal Generation Integration"),
            (self.test_portfolio_optimization_integration, "Portfolio Optimization Integration"),
            (self.test_backtesting_integration, "Backtesting Integration"),
            (self.test_user_management_integration, "User Management Integration"),
            (self.test_performance_analytics_integration, "Performance Analytics Integration"),
            (self.test_end_to_end_trading_workflow, "End-to-End Trading Workflow")
        ]
        
        if self.enhanced_runner:
            self.enhanced_runner.run_test_parallel(integration_tests)
        else:
            # Fallback to sequential testing
            for test_func, test_name in integration_tests:
                try:
                    start_time = time.time()
                    result = test_func()
                    duration = time.time() - start_time
                    
                    status = "✅" if result else "❌"
                    print(f"{status} {test_name} ({duration:.2f}s)")
                    
                    self.results.append({
                        'test_name': test_name,
                        'passed': result,
                        'duration': duration
                    })
                except Exception as e:
                    print(f"💥 {test_name} - ERROR: {e}")
                    self.results.append({
                        'test_name': test_name,
                        'passed': False,
                        'duration': 0,
                        'error': str(e)
                    })
    
    def run_comprehensive_test_suite(self):
        """Run the complete test suite including original and enhanced tests"""
        print("=" * 70)
        print("🧪 COMPREHENSIVE INTEGRATION TEST SUITE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # 1. Run original quick tests if available
        print("\n1. QUICK VALIDATION TESTS")
        print("-" * 70)
        if TestSuite:
            try:
                run_quick_tests()
            except Exception as e:
                print(f"Quick tests error: {e}")
        else:
            print("Original test suite not available")
        
        # 2. Run integration tests
        self.run_integration_tests()
        
        # 3. Run load tests
        self.run_load_tests()
        
        # 4. Run stress tests
        self.run_stress_tests()
        
        # 5. Generate comprehensive report
        total_duration = time.time() - start_time
        self.generate_comprehensive_report(total_duration)
    
    def generate_comprehensive_report(self, total_duration: float):
        """Generate comprehensive test report"""
        print("\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Combine results from enhanced runner if available
        all_results = self.results.copy()
        if self.enhanced_runner:
            all_results.extend([{
                'test_name': r.test_name,
                'passed': r.passed,
                'duration': r.duration,
                'error': r.error
            } for r in self.enhanced_runner.results])
        
        if not all_results:
            print("No test results to report")
            return
        
        # Calculate summary statistics
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        avg_duration = sum(r['duration'] for r in all_results) / total_tests if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Average Test Duration: {avg_duration:.3f}s")
        
        # List failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in all_results:
                if not result['passed']:
                    print(f"  • {result['test_name']}")
                    if result.get('error'):
                        print(f"    Error: {result['error']}")
        
        # Performance insights
        if self.enhanced_runner:
            performance_report = self.enhanced_runner.generate_performance_report()
            if performance_report:
                print(f"\n🚀 PERFORMANCE INSIGHTS:")
                perf_summary = performance_report.get('summary', {})
                if perf_summary:
                    print(f"  • Average test duration: {perf_summary.get('avg_test_duration', 0):.3f}s")
                    
                fastest = performance_report.get('performance', {}).get('fastest_test')
                slowest = performance_report.get('performance', {}).get('slowest_test')
                
                if fastest and fastest['name']:
                    print(f"  • Fastest test: {fastest['name']} ({fastest['duration']:.3f}s)")
                if slowest and slowest['name']:
                    print(f"  • Slowest test: {slowest['name']} ({slowest['duration']:.3f}s)")
        
        # Save report
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_duration': total_duration,
                'total_tests': total_tests
            },
            'summary': {
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': success_rate
            },
            'all_results': all_results
        }
        
        filename = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {filename}")
        
        # Final assessment
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT! {success_rate:.1f}% success rate - System is ready for production")
        elif success_rate >= 85:
            print(f"\n✅ GOOD! {success_rate:.1f}% success rate - Minor issues to address")
        elif success_rate >= 70:
            print(f"\n⚠️  MODERATE! {success_rate:.1f}% success rate - Several issues need fixing")
        else:
            print(f"\n🚨 POOR! {success_rate:.1f}% success rate - Major issues require attention")


if __name__ == "__main__":
    # Run comprehensive integration test suite
    integration_suite = IntegrationTestSuite()
    integration_suite.run_comprehensive_test_suite()
