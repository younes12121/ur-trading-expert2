"""
Enhanced Test Runner with Performance Monitoring and Detailed Reporting
Provides comprehensive testing with performance metrics, memory usage, and detailed reports
"""

import sys
import os
import time
import psutil
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import concurrent.futures
import traceback
from contextlib import contextmanager

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class PerformanceMonitor:
    """Monitor performance metrics during test execution"""
    
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'timestamps': []
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Monitor system metrics in background"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                
                self.metrics['cpu_usage'].append(cpu_percent)
                self.metrics['memory_usage'].append(memory_info.percent)
                self.metrics['timestamps'].append(time.time())
                
                time.sleep(0.5)
            except Exception:
                break
    
    def get_summary(self):
        """Get performance summary"""
        if not self.metrics['cpu_usage']:
            return {}
        
        return {
            'avg_cpu': sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage']),
            'max_cpu': max(self.metrics['cpu_usage']),
            'avg_memory': sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage']),
            'max_memory': max(self.metrics['memory_usage']),
            'samples': len(self.metrics['cpu_usage'])
        }


class EnhancedTestResult:
    """Enhanced test result with performance metrics"""
    
    def __init__(self, test_name: str, passed: bool, duration: float = 0.0, 
                 message: str = "", error: str = "", performance: Dict = None):
        self.test_name = test_name
        self.passed = passed
        self.duration = duration
        self.message = message
        self.error = error
        self.performance = performance or {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class EnhancedTestRunner:
    """Enhanced test runner with performance monitoring and parallel execution"""
    
    def __init__(self, max_workers: int = 4):
        self.results: List[EnhancedTestResult] = []
        self.max_workers = max_workers
        self.performance_monitor = PerformanceMonitor()
        self.test_user_id = 999999
        
    @contextmanager
    def monitor_test(self, test_name: str):
        """Context manager for monitoring individual tests"""
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        
        try:
            yield
            success = True
        except Exception as e:
            success = False
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.virtual_memory().percent
            
            performance = {
                'duration': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'success': success
            }
    
    def run_test_parallel(self, test_functions: List[tuple], max_workers: int = None):
        """Run tests in parallel for better performance"""
        if max_workers is None:
            max_workers = self.max_workers
        
        print(f"🚀 Running {len(test_functions)} tests in parallel (max {max_workers} workers)")
        print("-" * 70)
        
        self.performance_monitor.start_monitoring()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self._run_single_test, test_func, test_name): test_name
                for test_func, test_name in test_functions
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    status = "✅" if result.passed else "❌"
                    print(f"{status} {test_name} ({result.duration:.2f}s)")
                except Exception as e:
                    error_result = EnhancedTestResult(
                        test_name, False, 0.0, "Test crashed", str(e)
                    )
                    self.results.append(error_result)
                    print(f"💥 {test_name} - CRASHED: {e}")
        
        self.performance_monitor.stop_monitoring()
        
    def _run_single_test(self, test_func, test_name: str) -> EnhancedTestResult:
        """Run a single test with performance monitoring"""
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        
        try:
            result = test_func()
            success = bool(result)
            message = "Test passed" if success else "Test failed"
            error = ""
        except Exception as e:
            success = False
            message = "Test crashed"
            error = str(e)
        
        end_time = time.time()
        duration = end_time - start_time
        end_memory = psutil.virtual_memory().percent
        
        performance = {
            'duration': duration,
            'memory_delta': end_memory - start_memory
        }
        
        return EnhancedTestResult(
            test_name=test_name,
            passed=success,
            duration=duration,
            message=message,
            error=error,
            performance=performance
        )
    
    def run_load_test(self, test_func, test_name: str, iterations: int = 100):
        """Run load test with multiple iterations"""
        print(f"🔥 Load Testing: {test_name} ({iterations} iterations)")
        print("-" * 70)
        
        results = []
        self.performance_monitor.start_monitoring()
        
        for i in range(iterations):
            start_time = time.time()
            try:
                test_func()
                success = True
                error = ""
            except Exception as e:
                success = False
                error = str(e)
            
            duration = time.time() - start_time
            results.append({
                'iteration': i + 1,
                'success': success,
                'duration': duration,
                'error': error
            })
            
            # Progress update
            if (i + 1) % 10 == 0:
                success_rate = sum(1 for r in results if r['success']) / len(results) * 100
                avg_duration = sum(r['duration'] for r in results) / len(results)
                print(f"  Progress: {i+1}/{iterations} - Success: {success_rate:.1f}% - Avg: {avg_duration:.3f}s")
        
        self.performance_monitor.stop_monitoring()
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            avg_duration = sum(r['duration'] for r in successful) / len(successful)
            min_duration = min(r['duration'] for r in successful)
            max_duration = max(r['duration'] for r in successful)
        else:
            avg_duration = min_duration = max_duration = 0
        
        load_test_result = {
            'total_iterations': iterations,
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / iterations * 100,
            'avg_duration': avg_duration,
            'min_duration': min_duration,
            'max_duration': max_duration,
            'performance_summary': self.performance_monitor.get_summary()
        }
        
        self.results.append(EnhancedTestResult(
            test_name=f"Load Test: {test_name}",
            passed=len(failed) == 0,
            duration=sum(r['duration'] for r in results),
            message=f"Success rate: {load_test_result['success_rate']:.1f}%",
            performance=load_test_result
        ))
        
        return load_test_result
    
    def run_stress_test(self, test_functions: List[tuple], concurrent_users: int = 10):
        """Simulate multiple concurrent users"""
        print(f"⚡ Stress Testing with {concurrent_users} concurrent users")
        print("-" * 70)
        
        self.performance_monitor.start_monitoring()
        start_time = time.time()
        
        def user_session():
            """Simulate a user session running all tests"""
            session_results = []
            for test_func, test_name in test_functions:
                try:
                    result = test_func()
                    session_results.append({'test': test_name, 'success': bool(result)})
                except Exception as e:
                    session_results.append({'test': test_name, 'success': False, 'error': str(e)})
            return session_results
        
        # Run concurrent user sessions
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_session) for _ in range(concurrent_users)]
            all_session_results = []
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    session_result = future.result()
                    all_session_results.extend(session_result)
                except Exception as e:
                    print(f"❌ User session failed: {e}")
        
        self.performance_monitor.stop_monitoring()
        total_duration = time.time() - start_time
        
        # Analyze stress test results
        total_tests = len(all_session_results)
        successful_tests = sum(1 for r in all_session_results if r['success'])
        
        stress_result = {
            'concurrent_users': concurrent_users,
            'total_tests_run': total_tests,
            'successful_tests': successful_tests,
            'overall_success_rate': successful_tests / total_tests * 100 if total_tests > 0 else 0,
            'total_duration': total_duration,
            'performance_summary': self.performance_monitor.get_summary()
        }
        
        self.results.append(EnhancedTestResult(
            test_name="Stress Test",
            passed=stress_result['overall_success_rate'] > 95,  # Pass if >95% success
            duration=total_duration,
            message=f"Success rate: {stress_result['overall_success_rate']:.1f}%",
            performance=stress_result
        ))
        
        return stress_result
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        if not self.results:
            return {}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        total_duration = sum(r.duration for r in self.results)
        
        # Performance metrics
        durations = [r.duration for r in self.results if r.duration > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            fastest_test = min(self.results, key=lambda x: x.duration if x.duration > 0 else float('inf'))
            slowest_test = max(self.results, key=lambda x: x.duration)
        else:
            avg_duration = 0
            fastest_test = slowest_test = None
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'success_rate': passed_tests / total_tests * 100 if total_tests > 0 else 0,
                'total_duration': total_duration,
                'avg_test_duration': avg_duration
            },
            'performance': {
                'fastest_test': {
                    'name': fastest_test.test_name if fastest_test else None,
                    'duration': fastest_test.duration if fastest_test else 0
                },
                'slowest_test': {
                    'name': slowest_test.test_name if slowest_test else None,
                    'duration': slowest_test.duration if slowest_test else 0
                }
            },
            'failed_tests': [
                {
                    'name': r.test_name,
                    'error': r.error,
                    'duration': r.duration
                }
                for r in self.results if not r.passed
            ]
        }
        
        return report
    
    def save_detailed_report(self, filename: str = None):
        """Save detailed test report to JSON"""
        if filename is None:
            filename = f"enhanced_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.results),
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
                    'python_version': sys.version
                }
            },
            'performance_report': self.generate_performance_report(),
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'duration': r.duration,
                    'message': r.message,
                    'error': r.error,
                    'performance': r.performance,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📊 Detailed report saved to: {filename}")
        return filename


# Test functions for demonstration
def sample_fast_test():
    """Fast test that should complete quickly"""
    time.sleep(0.01)
    return True

def sample_slow_test():
    """Slower test for performance comparison"""
    time.sleep(0.5)
    return True

def sample_memory_test():
    """Test that uses some memory"""
    # Create some data to use memory
    data = [i for i in range(10000)]
    return len(data) == 10000

def sample_failing_test():
    """Test that should fail"""
    return False


if __name__ == "__main__":
    # Demonstration of enhanced test runner
    runner = EnhancedTestRunner(max_workers=4)
    
    # Define test functions
    test_functions = [
        (sample_fast_test, "Fast Test"),
        (sample_slow_test, "Slow Test"),
        (sample_memory_test, "Memory Test"),
        (sample_failing_test, "Failing Test")
    ]
    
    print("=" * 70)
    print("🚀 ENHANCED TEST RUNNER DEMONSTRATION")
    print("=" * 70)
    
    # Run parallel tests
    print("\n1. PARALLEL TESTING")
    runner.run_test_parallel(test_functions)
    
    # Run load test
    print("\n2. LOAD TESTING")
    runner.run_load_test(sample_fast_test, "Fast Test Load", iterations=50)
    
    # Run stress test
    print("\n3. STRESS TESTING")
    runner.run_stress_test(test_functions[:3], concurrent_users=5)  # Exclude failing test
    
    # Generate and display report
    print("\n4. PERFORMANCE REPORT")
    print("=" * 70)
    report = runner.generate_performance_report()
    
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Total Duration: {report['summary']['total_duration']:.2f}s")
    print(f"Average Test Duration: {report['summary']['avg_test_duration']:.3f}s")
    
    if report['performance']['fastest_test']['name']:
        print(f"Fastest Test: {report['performance']['fastest_test']['name']} ({report['performance']['fastest_test']['duration']:.3f}s)")
        print(f"Slowest Test: {report['performance']['slowest_test']['name']} ({report['performance']['slowest_test']['duration']:.3f}s)")
    
    # Save detailed report
    runner.save_detailed_report()
    
    print("\n✅ Enhanced test runner demonstration complete!")
