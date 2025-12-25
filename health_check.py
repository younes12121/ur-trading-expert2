#!/usr/bin/env python3
"""
Trading System Health Check
Verifies all optimized components are working correctly
Enhanced with comprehensive performance monitoring
"""

import sys
import os
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class HealthChecker:
    """Comprehensive health checker with performance monitoring"""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.process = psutil.Process()

    def run_checks(self, comprehensive: bool = False) -> Dict:
        """Run all health checks"""
        self.start_time = datetime.now()
        self.results = {}

        print(f"Running health checks at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Core component checks
        self.results['components'] = self.check_optimized_components()
        self.results['config'] = self.check_config()
        self.results['performance_mode'] = self.check_performance_mode_status()

        # System resource checks
        self.results['system_resources'] = self.check_system_resources()
        self.results['memory_usage'] = self.check_memory_usage()
        self.results['cpu_usage'] = self.check_cpu_usage()

        # Performance checks
        self.results['cache_effectiveness'] = self.check_cache_effectiveness()
        self.results['api_rate_limits'] = self.check_api_rate_limits()
        self.results['performance'] = self.check_performance()

        if comprehensive:
            # Additional comprehensive checks
            self.results['concurrent_processing'] = self.check_concurrent_processing()
            self.results['memory_optimizer'] = self.check_memory_optimizer()
            self.results['error_rates'] = self.check_error_rates()
            self.results['data_integrity'] = self.check_data_integrity()
            self.results['network_connectivity'] = self.check_network_connectivity()

        self.results['timestamp'] = datetime.now().isoformat()
        self.results['duration'] = (datetime.now() - self.start_time).total_seconds()

        return self.results

    def check_optimized_components(self) -> Dict:
        """Check if optimized components can be imported and initialized with performance metrics"""
        components = [
            ("backtest_engine", "BacktestEngine"),
            ("data_fetcher", "BinanceDataFetcher"),
            ("elite_signal_generator", "EliteAPlusSignalGenerator"),
            ("ai_neural_predictor", "NeuralPredictor"),
            ("concurrent_processor", "ConcurrentProcessor"),
            ("memory_optimizer", "MemoryOptimizer"),
            ("performance_dashboard", "PerformanceDashboard"),
            ("performance_alerts", "PerformanceAlerts")
        ]

        results = {
            'healthy': True,
            'components': {},
            'init_times': {},
            'average_time': 0.0,
            'warnings': []
        }

        init_times = {}

        for module_name, class_name in components:
            try:
                # Measure initialization time
                start_time = time.time()
                module = __import__(module_name)
                cls = getattr(module, class_name)

                # Try to initialize with performance mode
                if "performance_mode" in cls.__init__.__code__.co_varnames:
                    instance = cls(performance_mode=True)
                    perf_mode = True
                else:
                    instance = cls()
                    perf_mode = False

                init_time = time.time() - start_time
                init_times[class_name] = init_time

                results['components'][class_name] = {
                    'status': 'OK',
                    'init_time': init_time,
                    'performance_mode': perf_mode
                }

            except Exception as e:
                results['components'][class_name] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                results['healthy'] = False

        # Calculate statistics
        valid_times = [t for t in init_times.values() if t is not None]
        if valid_times:
            results['average_time'] = sum(valid_times) / len(valid_times)
            results['init_times'] = init_times

            if results['average_time'] > 1.0:
                results['warnings'].append(f"Slow initialization detected ({results['average_time']:.3f}s average)")

        return results

    def check_config(self) -> Dict:
        """Check if performance config is properly set"""
        try:
            import config

            performance_settings = [
                'PERFORMANCE_MODE',
                'ENABLE_CACHING',
                'CONCURRENT_API',
                'JIT_COMPILATION',
                'LOG_LEVEL',
                'DB_PATH'
            ]

            results = {
                'healthy': True,
                'settings': {},
                'missing': [],
                'warnings': []
            }

            for setting in performance_settings:
                if hasattr(config, setting):
                    value = getattr(config, setting)
                    results['settings'][setting] = value

                    # Check for recommended settings
                    if setting == 'PERFORMANCE_MODE' and not value:
                        results['warnings'].append("Performance mode is disabled")
                    if setting == 'LOG_LEVEL' and value.upper() not in ['INFO', 'WARNING', 'ERROR']:
                        results['warnings'].append(f"Log level {value} may be too verbose for production")
                else:
                    results['missing'].append(setting)
                    results['healthy'] = False

            if results['missing']:
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_performance(self) -> Dict:
        """Run quick performance test"""
        try:
            import numpy as np

            # Test vectorization performance
            start = time.time()
            data = np.random.random(100000)
            result = data * data + 1
            vector_time = time.time() - start

            results = {
                'healthy': vector_time < 0.01,
                'vectorization_time': vector_time,
                'data_size': len(data),
                'performance_rating': 'FAST' if vector_time < 0.01 else 'SLOW'
            }

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_performance_mode_status(self) -> Dict:
        """Check performance mode status and effectiveness"""
        try:
            import config

            settings = {
                'PERFORMANCE_MODE': getattr(config, 'PERFORMANCE_MODE', False),
                'ENABLE_CACHING': getattr(config, 'ENABLE_CACHING', False),
                'CONCURRENT_API': getattr(config, 'CONCURRENT_API', False),
                'JIT_COMPILATION': getattr(config, 'JIT_COMPILATION', False)
            }

            # Calculate optimization score
            optimized_count = sum(settings.values())
            total_settings = len(settings)
            optimization_score = optimized_count / total_settings

            results = {
                'healthy': optimization_score >= 0.75,  # At least 75% optimized
                'settings': settings,
                'optimization_score': optimization_score,
                'status': 'OPTIMIZED' if optimization_score >= 0.75 else 'PARTIALLY_OPTIMIZED'
            }

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent(interval=0.1)

            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = psutil.virtual_memory().percent

            results = {
                'healthy': True,
                'memory_mb': memory_mb,
                'memory_percent': memory_percent,
                'cpu_percent': cpu_percent,
                'warnings': []
            }

            # Check thresholds
            if memory_percent > 80:
                results['warnings'].append("High memory usage")
                results['healthy'] = False
            if cpu_percent > 80:
                results['warnings'].append("High CPU usage")
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_memory_usage(self) -> Dict:
        """Detailed memory usage analysis"""
        try:
            import memory_optimizer
            optimizer = memory_optimizer.get_optimizer()
            stats = optimizer.get_memory_stats()

            results = {
                'healthy': True,
                'current_memory_mb': stats.get('current_memory_mb', 0),
                'peak_memory_mb': stats.get('peak_memory_mb', 0),
                'memory_limit_mb': stats.get('memory_threshold_mb', 500),
                'gc_collections': stats.get('gc_collections', 0),
                'warnings': []
            }

            # Check memory limits
            if results['current_memory_mb'] > results['memory_limit_mb']:
                results['warnings'].append(".2f")
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_cpu_usage(self) -> Dict:
        """CPU usage analysis"""
        try:
            cpu_percent = self.process.cpu_percent(interval=1.0)
            cpu_count = psutil.cpu_count()

            results = {
                'healthy': True,
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'warnings': []
            }

            if cpu_percent > 80:
                results['warnings'].append("High CPU usage detected")
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_cache_effectiveness(self) -> Dict:
        """Check cache effectiveness if available"""
        try:
            from data_fetcher import BinanceDataFetcher

            fetcher = BinanceDataFetcher(performance_mode=True)

            results = {
                'healthy': True,
                'cache_available': False,
                'cache_size': 0,
                'warnings': []
            }

            # Check if cache attributes exist
            if hasattr(fetcher, 'cache') and hasattr(fetcher, 'cache_time'):
                results['cache_available'] = True
                cache_size = len(fetcher.cache) if fetcher.cache else 0
                results['cache_size'] = cache_size

                if cache_size == 0:
                    results['warnings'].append("Cache is empty (will populate on use)")

            else:
                results['warnings'].append("Cache system not available")
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_api_rate_limits(self) -> Dict:
        """Check API rate limit status"""
        try:
            from data_fetcher import BinanceDataFetcher

            fetcher = BinanceDataFetcher(performance_mode=True)

            results = {
                'healthy': True,
                'rate_limit_tracked': False,
                'warnings': []
            }

            if hasattr(fetcher, 'request_count') and hasattr(fetcher, 'max_requests_per_minute'):
                rate = fetcher.request_count / fetcher.max_requests_per_minute if fetcher.max_requests_per_minute > 0 else 0
                results.update({
                    'rate_limit_tracked': True,
                    'request_count': fetcher.request_count,
                    'max_requests': fetcher.max_requests_per_minute,
                    'usage_percent': rate * 100
                })

                if rate > 0.8:
                    results['warnings'].append("Approaching API rate limit")
                    results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_concurrent_processing(self) -> Dict:
        """Check concurrent processing capabilities"""
        try:
            import concurrent_processor
            processor = concurrent_processor.get_processor()

            results = {
                'healthy': True,
                'processor_available': True,
                'active_tasks': processor.get_active_tasks(),
                'stats': processor.get_stats(),
                'warnings': []
            }

            # Check if processor is working
            if len(results['active_tasks']) > 0:
                results['warnings'].append(f"Active tasks detected: {len(results['active_tasks'])}")

            return results

        except Exception as e:
            return {
                'healthy': False,
                'processor_available': False,
                'error': str(e)
            }

    def check_memory_optimizer(self) -> Dict:
        """Check memory optimizer status"""
        try:
            import memory_optimizer
            optimizer = memory_optimizer.get_optimizer()

            results = {
                'healthy': True,
                'optimizer_available': True,
                'monitoring_active': optimizer.monitoring_active,
                'stats': optimizer.get_memory_stats(),
                'warnings': []
            }

            # Check if monitoring is active
            if not results['monitoring_active']:
                results['warnings'].append("Memory monitoring is not active")

            return results

        except Exception as e:
            return {
                'healthy': False,
                'optimizer_available': False,
                'error': str(e)
            }

    def check_error_rates(self) -> Dict:
        """Check error rates and system stability"""
        try:
            import performance_alerts
            alerts = performance_alerts.get_alerts()

            alert_summary = alerts.get_alert_summary()

            results = {
                'healthy': True,
                'alert_summary': alert_summary,
                'warnings': []
            }

            # Check for recent critical errors
            critical_alerts = [a for a in alert_summary.get('recent_alerts', [])
                             if a.get('level') == 'critical']

            if len(critical_alerts) > 0:
                results['warnings'].append(f"Critical alerts detected: {len(critical_alerts)}")
                results['healthy'] = False

            # Check error rate threshold
            error_rate = len([a for a in alert_summary.get('recent_alerts', [])
                            if a.get('level') in ['warning', 'critical']]) / max(len(alert_summary.get('recent_alerts', [])), 1)

            if error_rate > 0.05:  # 5% error rate
                results['warnings'].append(".1f")
                results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_data_integrity(self) -> Dict:
        """Check data integrity and database health"""
        try:
            import config
            import sqlite3

            results = {
                'healthy': True,
                'database_path': getattr(config, 'DB_PATH', 'trades.db'),
                'tables_checked': [],
                'warnings': []
            }

            # Check database file
            if not os.path.exists(results['database_path']):
                results['warnings'].append("Database file does not exist")
                results['healthy'] = False
                return results

            # Check database integrity
            conn = sqlite3.connect(results['database_path'])
            cursor = conn.cursor()

            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                results['tables_checked'].append(table_name)

                # Check table integrity
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                except Exception as e:
                    results['warnings'].append(f"Table {table_name} integrity check failed: {e}")
                    results['healthy'] = False

            conn.close()

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def check_network_connectivity(self) -> Dict:
        """Check network connectivity and API accessibility"""
        try:
            import requests

            results = {
                'healthy': True,
                'endpoints_checked': [],
                'warnings': []
            }

            # Test endpoints
            endpoints = [
                ('Binance API', 'https://api.binance.com/api/v3/ping'),
                ('Binance Testnet', 'https://testnet.binance.vision/api/v3/ping')
            ]

            for name, url in endpoints:
                try:
                    response = requests.get(url, timeout=5)
                    results['endpoints_checked'].append({
                        'name': name,
                        'url': url,
                        'status': response.status_code,
                        'accessible': response.status_code == 200
                    })

                    if response.status_code != 200:
                        results['warnings'].append(f"{name} returned status {response.status_code}")
                        results['healthy'] = False

                except Exception as e:
                    results['endpoints_checked'].append({
                        'name': name,
                        'url': url,
                        'status': 'ERROR',
                        'accessible': False,
                        'error': str(e)
                    })
                    results['warnings'].append(f"{name} not accessible: {e}")
                    results['healthy'] = False

            return results

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    def export_results(self, filename: Optional[str] = None) -> str:
        """Export health check results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_check_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        return filename

    def print_summary(self):
        """Print a formatted summary of health check results"""
        print("\n" + "="*80)
        print("HEALTH CHECK SUMMARY")
        print("="*80)

        if not self.results:
            print("No results available. Run checks first.")
            return

        duration = self.results.get('duration', 0)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Timestamp: {self.results.get('timestamp', 'Unknown')}")

        # Count results
        total_checks = len([k for k in self.results.keys() if k not in ['timestamp', 'duration']])
        healthy_checks = len([k for k, v in self.results.items()
                             if k not in ['timestamp', 'duration'] and v.get('healthy', False)])

        print(f"Checks passed: {healthy_checks}/{total_checks}")

        # Overall status
        overall_healthy = healthy_checks == total_checks
        status = "✅ ALL HEALTHY" if overall_healthy else "❌ ISSUES DETECTED"
        print(f"Overall status: {status}")

        if not overall_healthy:
            print("\nFAILED CHECKS:")
            for check_name, result in self.results.items():
                if check_name in ['timestamp', 'duration']:
                    continue
                if not result.get('healthy', True):
                    print(f"  • {check_name.upper()}")
                    if 'error' in result:
                        print(f"    Error: {result['error']}")
                    if 'warnings' in result and result['warnings']:
                        print(f"    Warnings: {', '.join(result['warnings'])}")

        return overall_healthy

def main():
    """Run all health checks"""
    import argparse

    parser = argparse.ArgumentParser(description='Trading System Health Check')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive checks including network and data integrity')
    parser.add_argument('--export', action='store_true',
                       help='Export results to JSON file')

    args = parser.parse_args()

    checker = HealthChecker()
    results = checker.run_checks(comprehensive=args.comprehensive)

    # Print detailed results
    print("\n" + "="*80)
    print("TRADING SYSTEM HEALTH CHECK")
    print("="*80)

    for check_name, result in results.items():
        if check_name in ['timestamp', 'duration']:
            continue

        status_icon = "✅" if result.get('healthy', False) else "❌"
        print(f"\n{status_icon} {check_name.upper()}")

        if 'error' in result:
            print(f"   Error: {result['error']}")
        elif 'warnings' in result and result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'])}")

        # Print key metrics
        if check_name == 'system_resources':
            print(".2f")
        elif check_name == 'memory_usage':
            print(".2f")
        elif check_name == 'cpu_usage':
            print(".1f")
        elif check_name == 'components':
            avg_time = result.get('average_time', 0)
            print(".3f")

    # Print summary
    overall_healthy = checker.print_summary()

    # Export if requested
    if args.export:
        filename = checker.export_results()
        print(f"\nResults exported to: {filename}")

    return overall_healthy

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
