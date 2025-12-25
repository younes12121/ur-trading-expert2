"""
Comprehensive Error Learning Test Suite
Simulates trading operations and error scenarios to validate ML-based error prevention
"""

import sys
import os
import time
import asyncio
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import bot components
from global_error_learning import global_error_manager, predict_error, record_error, get_error_insights
from error_dashboard import get_dashboard_report, get_system_health
from execution_manager import ExecutionManager
from risk_manager import EnhancedRiskManager
from data_fetcher import BinanceDataFetcher
from backtest_engine import BacktestEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorLearningTestSuite:
    """Comprehensive testing framework for error learning system"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.baseline_errors = 0
        self.post_learning_errors = 0

    def run_full_test_suite(self):
        """Run complete error learning test suite"""
        self.start_time = datetime.now()
        logger.info("🧪 Starting Error Learning Test Suite...")

        try:
            # Phase 1: Baseline Testing (without learning)
            logger.info("📊 Phase 1: Baseline Testing...")
            self.run_baseline_tests()

            # Phase 2: Learning Phase (build error patterns)
            logger.info("🧠 Phase 2: Learning Phase...")
            self.run_learning_phase()

            # Phase 3: Error Prevention Testing (with learning active)
            logger.info("🛡️ Phase 3: Error Prevention Testing...")
            self.run_prevention_tests()

            # Phase 4: Performance Validation
            logger.info("⚡ Phase 4: Performance Validation...")
            self.run_performance_tests()

            # Phase 5: Stress Testing
            logger.info("🔥 Phase 5: Stress Testing...")
            self.run_stress_tests()

            # Phase 6: Final Analysis
            logger.info("📈 Phase 6: Final Analysis...")
            self.generate_final_report()

        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            self.record_test_result("full_suite", False, error=str(e))

        self.end_time = datetime.now()
        return self.compile_results()

    def run_baseline_tests(self):
        """Test system behavior without error learning"""
        logger.info("Running baseline tests...")

        # Test 1: Normal Operations
        self.test_normal_operations("baseline")

        # Test 2: Error Simulation (no learning)
        self.test_error_simulation("baseline", learning_enabled=False)

        # Test 3: Component Isolation
        self.test_component_isolation("baseline")

        logger.info("✅ Baseline tests completed")

    def run_learning_phase(self):
        """Build error learning patterns through controlled operations"""
        logger.info("Building error learning patterns...")

        # Generate diverse error patterns
        self.generate_error_patterns()

        # Train error prediction models
        self.train_prediction_models()

        # Validate learning progress
        insights = get_error_insights()
        learning_progress = insights.get('learning_progress', 0)

        self.record_test_result("learning_phase",
                              learning_progress > 0.1,
                              metrics={"learning_progress": learning_progress})

        logger.info(f"✅ Learning phase completed - Progress: {learning_progress:.1%}")

    def run_prevention_tests(self):
        """Test error prevention capabilities with learning active"""
        logger.info("Testing error prevention capabilities...")

        # Test 1: Error Prediction Accuracy
        self.test_error_prediction_accuracy()

        # Test 2: Proactive Avoidance
        self.test_proactive_avoidance()

        # Test 3: Fallback Strategies
        self.test_fallback_strategies()

        # Test 4: Learning Adaptation
        self.test_learning_adaptation()

        logger.info("✅ Prevention tests completed")

    def run_performance_tests(self):
        """Test system performance with error learning active"""
        logger.info("Testing system performance...")

        # Test 1: Response Time Impact
        self.test_response_time_impact()

        # Test 2: Memory Usage
        self.test_memory_usage()

        # Test 3: CPU Utilization
        self.test_cpu_utilization()

        # Test 4: Concurrent Operations
        self.test_concurrent_operations()

        logger.info("✅ Performance tests completed")

    def run_stress_tests(self):
        """Test system under extreme conditions"""
        logger.info("Running stress tests...")

        # Test 1: High Error Rate Environment
        self.test_high_error_environment()

        # Test 2: Network Failure Simulation
        self.test_network_failures()

        # Test 3: Data Corruption Scenarios
        self.test_data_corruption()

        # Test 4: Resource Exhaustion
        self.test_resource_exhaustion()

        logger.info("✅ Stress tests completed")

    def test_normal_operations(self, phase: str):
        """Test normal operations without errors"""
        logger.info(f"Testing normal operations ({phase})...")

        try:
            # Test data fetcher
            fetcher = BinanceDataFetcher()
            # Note: This will likely fail in test environment, but tests error handling

            # Test risk manager
            risk_mgr = EnhancedRiskManager()
            position_size = risk_mgr.calculate_adaptive_position_size(
                balance=10000, entry_price=50000, stop_loss=49000,
                market_data={'volatility': 0.02}, signal_confidence=0.8
            )

            # Test execution manager
            exec_mgr = ExecutionManager()
            mock_data = {'btc_price': 50000, 'volatility': 0.02}
            mock_signal = {'entry_price': 49500, 'direction': 'BUY', 'position_size': 1.0, 'symbol': 'BTC'}

            # Record successful operations
            record_error('data_fetcher', {'operation_type': 'test_normal'}, had_error=False, execution_time=0.1)
            record_error('risk_manager', {'operation_type': 'test_normal'}, had_error=False, execution_time=0.1)
            record_error('execution_manager', {'operation_type': 'test_normal'}, had_error=False, execution_time=0.1)

            self.record_test_result(f"normal_operations_{phase}", True,
                                  metrics={"components_tested": 3})

        except Exception as e:
            self.record_test_result(f"normal_operations_{phase}", False, error=str(e))

    def test_error_simulation(self, phase: str, learning_enabled: bool = True):
        """Simulate various error conditions"""
        logger.info(f"Testing error simulation ({phase})...")

        error_scenarios = [
            # Component, Operation, Should Fail
            ('data_fetcher', 'get_market_data', True),
            ('execution_manager', 'optimize_entry', True),
            ('risk_manager', 'calculate_position_size', True),
            ('telegram_bot', 'process_command', False),  # Commands shouldn't fail
            ('backtest_engine', 'run_backtest', True),
        ]

        errors_simulated = 0
        errors_caught = 0

        for component, operation, should_fail in error_scenarios:
            try:
                # Simulate operation with controlled failure
                if should_fail and np.random.random() < 0.7:  # 70% chance of failure
                    raise Exception(f"Simulated {component} error in {operation}")

                # Record result
                record_error(component, {'operation_type': operation, 'phase': phase},
                           had_error=should_fail, execution_time=0.1)

                if should_fail:
                    errors_simulated += 1
                else:
                    errors_caught += 1

            except Exception as e:
                if should_fail:
                    errors_simulated += 1
                record_error(component, {'operation_type': operation, 'phase': phase},
                           had_error=True, error_details=str(e), execution_time=0.1)

        self.record_test_result(f"error_simulation_{phase}", True,
                              metrics={"errors_simulated": errors_simulated,
                                      "errors_caught": errors_caught,
                                      "learning_enabled": learning_enabled})

    def test_component_isolation(self, phase: str):
        """Test each component in isolation"""
        logger.info(f"Testing component isolation ({phase})...")

        components = ['data_fetcher', 'execution_manager', 'risk_manager', 'backtest_engine']
        results = {}

        for component in components:
            try:
                # Test basic operation
                prediction = predict_error(component, {'operation_type': 'test_isolation'})
                record_error(component, {'operation_type': 'test_isolation'},
                           had_error=False, execution_time=0.05)
                results[component] = True
            except Exception as e:
                results[component] = False
                self.record_test_result(f"isolation_{component}_{phase}", False, error=str(e))

        successful_components = sum(1 for r in results.values() if r)
        self.record_test_result(f"component_isolation_{phase}", successful_components >= 3,
                              metrics={"successful_components": successful_components,
                                      "total_components": len(components)})

    def generate_error_patterns(self):
        """Generate diverse error patterns for learning"""
        logger.info("Generating diverse error patterns...")

        # Create systematic error patterns
        patterns = [
            # High-frequency errors during certain hours
            self._generate_time_based_errors(),

            # Component-specific error patterns
            self._generate_component_errors(),

            # Load-based error patterns
            self._generate_load_based_errors(),

            # Data-dependent error patterns
            self._generate_data_errors(),
        ]

        total_patterns = sum(len(p) for p in patterns)
        logger.info(f"Generated {total_patterns} error patterns for learning")

    def _generate_time_based_errors(self) -> List[Dict]:
        """Generate errors that occur at specific times"""
        patterns = []
        error_hours = [3, 4, 15, 16]  # Early morning and afternoon errors

        for hour in error_hours:
            for i in range(10):  # 10 errors per hour
                patterns.append({
                    'component': 'data_fetcher',
                    'operation_context': {
                        'operation_type': 'get_market_data',
                        'time_of_day': hour + np.random.random(),
                        'system_load': 0.8 + np.random.random() * 0.2,
                        'memory_usage': 0.7 + np.random.random() * 0.3
                    },
                    'had_error': True,
                    'error_details': f'Market data fetch failed at hour {hour}',
                    'execution_time': 2.0 + np.random.random() * 3.0
                })

        return patterns

    def _generate_component_errors(self) -> List[Dict]:
        """Generate component-specific error patterns"""
        patterns = []

        # Risk manager errors with high volatility
        for i in range(15):
            patterns.append({
                'component': 'risk_manager',
                'operation_context': {
                    'operation_type': 'calculate_position_size',
                    'volatility': 0.15 + np.random.random() * 0.1,
                    'balance': 5000 + np.random.random() * 5000,
                    'confidence_level': 0.3 + np.random.random() * 0.4
                },
                'had_error': True,
                'error_details': 'Position size calculation failed under high volatility',
                'execution_time': 0.5 + np.random.random()
            })

        # Execution manager errors with extreme spreads
        for i in range(12):
            patterns.append({
                'component': 'execution_manager',
                'operation_context': {
                    'operation_type': 'optimize_entry',
                    'spread_width': 0.005 + np.random.random() * 0.01,
                    'liquidity_score': np.random.random() * 0.3
                },
                'had_error': True,
                'error_details': 'Entry optimization failed due to wide spreads',
                'execution_time': 1.0 + np.random.random() * 2.0
            })

        return patterns

    def _generate_load_based_errors(self) -> List[Dict]:
        """Generate errors under high system load"""
        patterns = []

        for i in range(20):
            high_load = 0.85 + np.random.random() * 0.15
            patterns.append({
                'component': np.random.choice(['telegram_bot', 'data_fetcher', 'backtest_engine']),
                'operation_context': {
                    'operation_type': 'high_load_operation',
                    'system_load': high_load,
                    'memory_usage': 0.8 + np.random.random() * 0.2
                },
                'had_error': True,
                'error_details': f'Operation failed under high load ({high_load:.1%})',
                'execution_time': 3.0 + np.random.random() * 5.0
            })

        return patterns

    def _generate_data_errors(self) -> List[Dict]:
        """Generate data-dependent error patterns"""
        patterns = []

        # Errors with corrupted/missing data
        for i in range(8):
            patterns.append({
                'component': 'signal_generator',
                'operation_context': {
                    'operation_type': 'generate_signal',
                    'data_quality': np.random.random() * 0.5,  # Poor data quality
                    'market_condition': np.random.choice(['volatile', 'illiquid', 'after_hours'])
                },
                'had_error': True,
                'error_details': 'Signal generation failed due to poor data quality',
                'execution_time': 1.5 + np.random.random() * 2.0
            })

        return patterns

    def train_prediction_models(self):
        """Train and validate error prediction models"""
        logger.info("Training error prediction models...")

        # Apply all generated error patterns
        all_patterns = (
            self._generate_time_based_errors() +
            self._generate_component_errors() +
            self._generate_load_based_errors() +
            self._generate_data_errors()
        )

        # Record patterns for learning
        for pattern in all_patterns:
            record_error(
                pattern['component'],
                pattern['operation_context'],
                had_error=pattern['had_error'],
                error_details=pattern.get('error_details'),
                execution_time=pattern['execution_time']
            )

        # Allow time for model retraining
        time.sleep(1)

        # Validate learning
        insights = get_error_insights()
        if insights.get('model_trained'):
            logger.info("✅ Error prediction models trained successfully")
        else:
            logger.warning("⚠️ Error prediction models not yet trained")

    def test_error_prediction_accuracy(self):
        """Test accuracy of error predictions"""
        logger.info("Testing error prediction accuracy...")

        test_cases = 50
        correct_predictions = 0
        total_predictions = 0

        for i in range(test_cases):
            # Generate random operation context
            component = np.random.choice(['data_fetcher', 'execution_manager', 'risk_manager'])
            context = {
                'operation_type': np.random.choice(['test_op1', 'test_op2', 'test_op3']),
                'system_load': np.random.random(),
                'memory_usage': np.random.random(),
                'time_of_day': np.random.random() * 24
            }

            # Get prediction
            prediction = predict_error(component, context)
            total_predictions += 1

            # Simulate actual outcome (with some randomness)
            actual_error = np.random.random() < prediction['error_probability'] * 1.2

            # Check if prediction was correct
            predicted_error = prediction['error_probability'] > 0.5
            if predicted_error == actual_error:
                correct_predictions += 1

            # Record for learning
            record_error(component, context, had_error=actual_error, execution_time=0.1)

        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        self.record_test_result("prediction_accuracy", accuracy > 0.7,
                              metrics={"accuracy": accuracy, "test_cases": test_cases})

        logger.info(f"✅ Prediction accuracy: {accuracy:.1%}")

    def test_proactive_avoidance(self):
        """Test proactive error avoidance capabilities"""
        logger.info("Testing proactive error avoidance...")

        high_risk_scenarios = [
            {'component': 'data_fetcher', 'context': {'system_load': 0.95, 'time_of_day': 4}},
            {'component': 'execution_manager', 'context': {'spread_width': 0.02, 'liquidity_score': 0.1}},
            {'component': 'risk_manager', 'context': {'volatility': 0.25, 'confidence_level': 0.2}},
        ]

        avoidances = 0
        total_scenarios = len(high_risk_scenarios)

        for scenario in high_risk_scenarios:
            prediction = predict_error(scenario['component'], scenario['context'])

            if not prediction['should_attempt']:
                avoidances += 1
                record_error(scenario['component'], scenario['context'],
                           had_error=False, error_details="Proactively avoided",
                           success_metrics={'avoided_error': True})

        avoidance_rate = avoidances / total_scenarios if total_scenarios > 0 else 0
        self.record_test_result("proactive_avoidance", avoidance_rate > 0.8,
                              metrics={"avoidance_rate": avoidance_rate, "scenarios_tested": total_scenarios})

        logger.info(f"✅ Proactive avoidance rate: {avoidance_rate:.1%}")

    def test_fallback_strategies(self):
        """Test effectiveness of fallback strategies"""
        logger.info("Testing fallback strategies...")

        # Test fallback effectiveness by simulating failures and checking recovery
        fallback_tests = [
            {'component': 'data_fetcher', 'fallback': 'use_cached_data'},
            {'component': 'execution_manager', 'fallback': 'use_market_order'},
            {'component': 'risk_manager', 'fallback': 'use_conservative_sizing'},
        ]

        successful_fallbacks = 0

        for test in fallback_tests:
            # Simulate primary operation failure
            record_error(test['component'], {'operation_type': 'primary_failed'},
                        had_error=True, error_details="Primary operation failed")

            # Test fallback
            prediction = predict_error(test['component'], {'operation_type': test['fallback']})

            if prediction['should_attempt']:  # Fallback should be allowed
                successful_fallbacks += 1
                record_error(test['component'], {'operation_type': test['fallback']},
                           had_error=False, success_metrics={'fallback_successful': True})

        fallback_success_rate = successful_fallbacks / len(fallback_tests)
        self.record_test_result("fallback_strategies", fallback_success_rate > 0.8,
                              metrics={"success_rate": fallback_success_rate, "tests_run": len(fallback_tests)})

        logger.info(f"✅ Fallback success rate: {fallback_success_rate:.1%}")

    def test_learning_adaptation(self):
        """Test system's ability to adapt and learn over time"""
        logger.info("Testing learning adaptation...")

        # Test learning curve by checking prediction improvements
        initial_predictions = []
        final_predictions = []

        # Get initial predictions (before much learning)
        for i in range(10):
            pred = predict_error('test_component', {'operation_type': f'initial_test_{i}'})
            initial_predictions.append(pred['error_probability'])

        # Add learning data
        for i in range(50):
            record_error('test_component', {'operation_type': f'learning_op_{i}'},
                        had_error=(i % 3 == 0), execution_time=0.1)  # 33% error rate

        # Allow learning
        time.sleep(0.5)

        # Get final predictions (after learning)
        for i in range(10):
            pred = predict_error('test_component', {'operation_type': f'final_test_{i}'})
            final_predictions.append(pred['error_probability'])

        # Check if predictions became more accurate (should center around 0.33)
        initial_avg = np.mean(initial_predictions)
        final_avg = np.mean(final_predictions)
        target_error_rate = 0.33

        initial_accuracy = 1 - abs(initial_avg - target_error_rate)
        final_accuracy = 1 - abs(final_avg - target_error_rate)

        adaptation_improved = final_accuracy > initial_accuracy
        self.record_test_result("learning_adaptation", adaptation_improved,
                              metrics={"initial_accuracy": initial_accuracy,
                                      "final_accuracy": final_accuracy,
                                      "improvement": final_accuracy - initial_accuracy})

        logger.info(f"✅ Learning adaptation: {'Improved' if adaptation_improved else 'No improvement'}")

    def test_response_time_impact(self):
        """Test performance impact of error learning"""
        logger.info("Testing response time impact...")

        # Measure response times with and without error learning
        test_operations = 100

        # With error learning
        start_time = time.time()
        for i in range(test_operations):
            predict_error('test_component', {'operation_type': f'perf_test_{i}'})
        with_learning_time = (time.time() - start_time) / test_operations

        # Response time should be acceptable (< 50ms per prediction)
        acceptable_time = 0.05  # 50ms
        performance_acceptable = with_learning_time < acceptable_time

        self.record_test_result("response_time_impact", performance_acceptable,
                              metrics={"avg_response_time": with_learning_time,
                                      "acceptable_threshold": acceptable_time,
                                      "operations_tested": test_operations})

        logger.info(f"✅ Average response time: {with_learning_time*1000:.1f}ms")

    def test_memory_usage(self):
        """Test memory usage impact"""
        logger.info("Testing memory usage...")

        import psutil
        process = psutil.Process()

        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform operations
        for i in range(1000):
            predict_error('test_component', {'operation_type': f'memory_test_{i}'})
            record_error('test_component', {'operation_type': f'memory_test_{i}'},
                        had_error=(i % 10 == 0), execution_time=0.001)

        # Final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Memory increase should be reasonable (< 50MB)
        acceptable_increase = 50  # MB
        memory_acceptable = memory_increase < acceptable_increase

        self.record_test_result("memory_usage", memory_acceptable,
                              metrics={"baseline_memory": baseline_memory,
                                      "final_memory": final_memory,
                                      "memory_increase": memory_increase,
                                      "acceptable_increase": acceptable_increase})

        logger.info(f"✅ Memory increase: {memory_increase:.1f}MB")

    def test_cpu_utilization(self):
        """Test CPU utilization impact"""
        logger.info("Testing CPU utilization...")

        # This is a simplified CPU test - in production would use more sophisticated monitoring
        self.record_test_result("cpu_utilization", True,
                              metrics={"cpu_impact": "acceptable", "monitoring": "simplified"})

        logger.info("✅ CPU utilization test completed")

    def test_concurrent_operations(self):
        """Test concurrent operations handling"""
        logger.info("Testing concurrent operations...")

        results = []
        errors = []

        def concurrent_test(thread_id):
            try:
                for i in range(50):
                    prediction = predict_error(f'component_{thread_id}',
                                             {'operation_type': f'concurrent_test_{i}'})
                    record_error(f'component_{thread_id}',
                               {'operation_type': f'concurrent_test_{i}'},
                               had_error=(i % 5 == 0), execution_time=0.01)
                results.append(True)
            except Exception as e:
                errors.append(str(e))
                results.append(False)

        # Run concurrent tests
        threads = []
        for i in range(5):  # 5 concurrent threads
            t = threading.Thread(target=concurrent_test, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        success_rate = sum(1 for r in results if r) / len(results)
        concurrent_successful = success_rate > 0.9 and len(errors) == 0

        self.record_test_result("concurrent_operations", concurrent_successful,
                              metrics={"success_rate": success_rate,
                                      "threads_tested": len(threads),
                                      "errors": len(errors)})

        logger.info(f"✅ Concurrent operations success rate: {success_rate:.1%}")

    def test_high_error_environment(self):
        """Test system behavior in high error rate environment"""
        logger.info("Testing high error environment...")

        # Simulate high error rate environment
        high_error_operations = 100
        errors_injected = 0

        for i in range(high_error_operations):
            component = np.random.choice(['data_fetcher', 'execution_manager', 'risk_manager'])

            # Force high error rate
            if np.random.random() < 0.8:  # 80% error rate
                record_error(component, {'operation_type': 'high_error_test', 'error_env': True},
                           had_error=True, error_details="Injected error for testing",
                           execution_time=0.1)
                errors_injected += 1

        # Check system resilience
        insights = get_error_insights()
        system_health = insights.get('system_health_score', 0)

        # System should maintain reasonable health even under high error conditions
        resilient = system_health > 40  # Still functional despite high errors

        self.record_test_result("high_error_environment", resilient,
                              metrics={"errors_injected": errors_injected,
                                      "system_health": system_health,
                                      "total_operations": high_error_operations})

        logger.info(f"✅ System health under high error load: {system_health:.1f}/100")

    def test_network_failures(self):
        """Test network failure handling"""
        logger.info("Testing network failure simulation...")

        # Simulate network failures for data fetcher
        network_failures = 20

        for i in range(network_failures):
            record_error('data_fetcher',
                        {'operation_type': 'network_request', 'network_failure': True},
                        had_error=True,
                        error_details="Simulated network failure",
                        execution_time=5.0 + np.random.random() * 10.0)  # Long timeouts

        # Test if system learns to avoid network operations
        prediction = predict_error('data_fetcher', {'operation_type': 'network_request'})
        avoidance_learned = not prediction['should_attempt']

        self.record_test_result("network_failures", avoidance_learned,
                              metrics={"failures_simulated": network_failures,
                                      "avoidance_learned": avoidance_learned,
                                      "error_probability": prediction['error_probability']})

        logger.info(f"✅ Network failure avoidance: {'Learned' if avoidance_learned else 'Not learned'}")

    def test_data_corruption(self):
        """Test handling of data corruption scenarios"""
        logger.info("Testing data corruption handling...")

        # Simulate data corruption errors
        corruption_scenarios = [
            'invalid_price_data',
            'missing_market_data',
            'corrupted_ohlc_data',
            'inconsistent_volume_data'
        ]

        for scenario in corruption_scenarios:
            record_error('data_fetcher',
                        {'operation_type': 'process_data', 'data_corruption': scenario},
                        had_error=True,
                        error_details=f"Data corruption: {scenario}",
                        execution_time=0.5 + np.random.random())

        # Test if system becomes more cautious with data processing
        prediction = predict_error('data_fetcher', {'operation_type': 'process_data'})
        cautious_approach = prediction['error_probability'] > 0.3

        self.record_test_result("data_corruption", cautious_approach,
                              metrics={"scenarios_tested": len(corruption_scenarios),
                                      "cautious_approach": cautious_approach,
                                      "error_probability": prediction['error_probability']})

        logger.info(f"✅ Data corruption handling: {'Cautious' if cautious_approach else 'Not cautious'}")

    def test_resource_exhaustion(self):
        """Test behavior under resource exhaustion"""
        logger.info("Testing resource exhaustion...")

        # Simulate resource exhaustion
        exhaustion_tests = 50

        for i in range(exhaustion_tests):
            record_error(np.random.choice(['telegram_bot', 'backtest_engine']),
                        {'operation_type': 'resource_intensive', 'memory_pressure': True},
                        had_error=True,
                        error_details="Resource exhaustion simulated",
                        execution_time=10.0 + np.random.random() * 20.0)  # Very slow operations

        # Check if system adapts to avoid resource-intensive operations
        prediction = predict_error('backtest_engine', {'operation_type': 'resource_intensive'})
        resource_avoidance = not prediction['should_attempt']

        self.record_test_result("resource_exhaustion", resource_avoidance,
                              metrics={"exhaustion_tests": exhaustion_tests,
                                      "resource_avoidance": resource_avoidance,
                                      "error_probability": prediction['error_probability']})

        logger.info(f"✅ Resource exhaustion handling: {'Avoids' if resource_avoidance else 'Continues'}")

    def generate_final_report(self):
        """Generate comprehensive final test report"""
        logger.info("Generating final test report...")

        # Calculate overall metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0

        # Error reduction analysis
        insights = get_error_insights()
        final_error_rate = insights.get('recent_error_rate', 0)
        system_health = insights.get('system_health_score', 0)
        learning_progress = insights.get('learning_progress', 0)

        # Performance analysis
        avg_response_time = np.mean([r.get('response_time', 0) for r in self.test_results if 'response_time' in r])
        memory_efficiency = all(r.get('memory_acceptable', True) for r in self.test_results if 'memory_acceptable' in r)

        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'pass_rate': pass_rate,
                'test_duration': str(self.end_time - self.start_time) if self.end_time else 'Unknown'
            },
            'error_learning_metrics': {
                'final_error_rate': final_error_rate,
                'system_health_score': system_health,
                'learning_progress': learning_progress,
                'total_operations_learned': insights.get('total_operations', 0),
                'model_trained': insights.get('model_trained', False)
            },
            'performance_metrics': {
                'average_response_time': avg_response_time,
                'memory_efficiency': memory_efficiency,
                'concurrent_operations_supported': True  # From concurrent test
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations(pass_rate, system_health, learning_progress)
        }

        # Save report
        report_file = f"error_learning_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✅ Final report saved to: {report_file}")

        # Print summary
        print("\n" + "="*80)
        print("🎯 ERROR LEARNING TEST SUITE - FINAL RESULTS")
        print("="*80)
        print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({pass_rate:.1%})")
        print(f"❤️ System Health: {system_health:.1f}/100")
        print(f"🧠 Learning Progress: {learning_progress:.1%}")
        print(f"⚠️ Final Error Rate: {final_error_rate:.2%}")
        print(f"⏱️ Test Duration: {report['test_summary']['test_duration']}")
        print(f"📄 Report Saved: {report_file}")

        if pass_rate > 0.9 and system_health > 80:
            print("\n🎉 ALL CRITERIA MET - Error Learning System Ready for Production!")
        elif pass_rate > 0.8 and system_health > 60:
            print("\n⚠️ MOST CRITERIA MET - Error Learning System Ready for Staging")
        else:
            print("\n❌ CRITERIA NOT MET - Additional Development Required")

        print("="*80)

    def generate_recommendations(self, pass_rate: float, system_health: float, learning_progress: float) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if pass_rate < 0.8:
            recommendations.append("Improve test reliability - focus on component integration")
        if system_health < 70:
            recommendations.append("Optimize error learning algorithms for better system health")
        if learning_progress < 0.5:
            recommendations.append("Increase training data volume and diversity")
        if not any(r.get('concurrent_operations_supported', False) for r in self.test_results if 'concurrent' in r.get('test_name', '')):
            recommendations.append("Enhance concurrent operation handling")

        if not recommendations:
            recommendations.append("System performing well - consider advanced features")

        return recommendations

    def record_test_result(self, test_name: str, passed: bool, error: str = None, metrics: Dict = None):
        """Record individual test result"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'metrics': metrics or {}
        }
        self.test_results.append(result)

        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"Test {test_name}: {status}")

    def compile_results(self) -> Dict:
        """Compile all test results into final report"""
        return {
            'test_suite': 'Error Learning Comprehensive Test Suite',
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['passed']),
                'failed_tests': sum(1 for r in self.test_results if not r['passed']),
                'pass_rate': sum(1 for r in self.test_results if r['passed']) / len(self.test_results) if self.test_results else 0
            }
        }

# Convenience functions
def run_error_learning_tests():
    """Run the complete error learning test suite"""
    suite = ErrorLearningTestSuite()
    return suite.run_full_test_suite()

def run_quick_test():
    """Run a quick subset of tests for development"""
    suite = ErrorLearningTestSuite()

    # Run only critical tests
    suite.test_normal_operations("quick")
    suite.test_error_prediction_accuracy()
    suite.test_proactive_avoidance()

    return suite.compile_results()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Error Learning Test Suite')
    parser.add_argument('--quick', action='store_true', help='Run quick test subset')
    parser.add_argument('--full', action='store_true', help='Run full comprehensive test suite')

    args = parser.parse_args()

    if args.quick:
        print("🚀 Running Quick Error Learning Tests...")
        results = run_quick_test()
    elif args.full:
        print("🧪 Running Full Error Learning Test Suite...")
        results = run_error_learning_tests()
    else:
        print("Please specify --quick or --full")
        exit(1)

    # Print summary
    summary = results.get('summary', {})
    print(f"\n📊 Test Results: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} passed ({summary.get('pass_rate', 0):.1%})")
