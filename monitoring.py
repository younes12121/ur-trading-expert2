"""
Production Monitoring and Logging System
Provides comprehensive monitoring, logging, and alerting for the trading bot
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import wraps
import time
import sys

# Optional dependency - 
# psutil for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# Configure structured logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class ProductionLogger:
    """Production-grade logging system"""
    
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup loggers
        self.setup_loggers(log_level)
        
        # Metrics tracking
        self.metrics = {
            'commands_executed': 0,
            'signals_generated': 0,
            'errors': 0,
            'warnings': 0,
            'api_calls': 0,
            'response_times': []
        }

    def log_info(self, message: str, data: Dict = None):
        """Generic info logging method"""
        # #region agent log - Hypothesis A: Missing log_info method
        try:
            import json
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cursor', 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"monitoring.py:47","message":"log_info method called","data":{"message":message,"data":data},"timestamp":int(__import__('time').time()*1000)}) + "\n")
        except: pass
        # #endregion

        self.app_logger.info(f"{message} - {data if data else ''}")
        
    def setup_loggers(self, log_level):
        """Setup multiple loggers for different purposes"""
        
        # Main application logger
        self.app_logger = logging.getLogger('trading_bot')
        self.app_logger.setLevel(log_level)
        
        # Error logger
        self.error_logger = logging.getLogger('trading_bot.errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # Performance logger
        self.perf_logger = logging.getLogger('trading_bot.performance')
        self.perf_logger.setLevel(logging.INFO)
        
        # Security logger
        self.security_logger = logging.getLogger('trading_bot.security')
        self.security_logger.setLevel(logging.WARNING)
        
        # Setup file handlers
        handlers = [
            logging.FileHandler(
                os.path.join(self.log_dir, 'app.log'),
                encoding='utf-8'
            ),
            logging.FileHandler(
                os.path.join(self.log_dir, 'errors.log'),
                encoding='utf-8'
            ),
            logging.FileHandler(
                os.path.join(self.log_dir, 'performance.log'),
                encoding='utf-8'
            ),
            logging.FileHandler(
                os.path.join(self.log_dir, 'security.log'),
                encoding='utf-8'
            )
        ]
        
        # Add console handler for development
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            handlers.append(logging.StreamHandler(sys.stdout))
        
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        
        for handler in handlers:
            handler.setFormatter(formatter)
            if 'errors.log' in handler.baseFilename:
                self.error_logger.addHandler(handler)
            elif 'performance.log' in handler.baseFilename:
                self.perf_logger.addHandler(handler)
            elif 'security.log' in handler.baseFilename:
                self.security_logger.addHandler(handler)
            else:
                self.app_logger.addHandler(handler)
    
    def log_command(self, command: str, user_id: int, success: bool = True, 
                    execution_time: float = None, error: str = None):
        """Log command execution"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'user_id': user_id,
            'success': success,
            'execution_time': execution_time
        }
        
        if error:
            log_data['error'] = error
            self.metrics['errors'] += 1
            self.error_logger.error(json.dumps(log_data))
        else:
            self.metrics['commands_executed'] += 1
            self.app_logger.info(json.dumps(log_data))
        
        if execution_time:
            self.metrics['response_times'].append(execution_time)
            if len(self.metrics['response_times']) > 1000:
                self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def log_signal(self, pair: str, direction: str, confidence: int):
        """Log signal generation"""
        self.metrics['signals_generated'] += 1
        self.app_logger.info(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'event': 'signal_generated',
            'pair': pair,
            'direction': direction,
            'confidence': confidence
        }))
    
    def log_error(self, error: Exception, context: Dict = None):
        """Log errors with context"""
        self.metrics['errors'] += 1
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.error_logger.error(json.dumps(error_data))
    
    def log_security_event(self, event_type: str, user_id: int = None, 
                          details: Dict = None):
        """Log security-related events"""
        self.security_logger.warning(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details or {}
        }))
    
    def log_performance(self, operation: str, duration: float, 
                       metadata: Dict = None):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_ms': duration * 1000,
            'metadata': metadata or {}
        }
        self.perf_logger.info(json.dumps(perf_data))
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        return {
            **self.metrics,
            'avg_response_time': avg_response_time,
            'system_metrics': self.get_system_metrics()
        }
    
    def get_system_metrics(self) -> Dict:
        """Get system resource metrics"""
        if not PSUTIL_AVAILABLE:
            return {'note': 'psutil not available - install with: pip install psutil'}
        
        try:
            process = psutil.Process()
            return {
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'threads': process.num_threads(),
                'open_files': len(process.open_files())
            }
        except:
            return {}


class PerformanceMonitor:
    """Monitor and track performance metrics with optimization tracking"""
    
    def __init__(self, logger: ProductionLogger):
        self.logger = logger
        self.start_times = {}
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'concurrent_operations': 0,
            'optimization_usage': {},
            'memory_usage': [],
            'cpu_usage': [],
            'performance_mode_enabled': False,
            'concurrent_tasks_active': 0,
            'memory_optimization_active': False,
            'cache_effectiveness': 0.0,
            'avg_response_time': 0.0
        }
        
        # Try to import performance alerts
        try:
            from performance_alerts import get_alerts, check_performance_metrics
            self.alerts = get_alerts()
            self.check_metrics = check_performance_metrics
            self.alerts_enabled = True
        except ImportError:
            self.alerts = None
            self.check_metrics = None
            self.alerts_enabled = False
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str, metadata: Dict = None):
        """End timing and log"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.logger.log_performance(operation, duration, metadata)
            del self.start_times[operation]
            return duration
        return None
    
    def timed_operation(self, operation_name: str):
        """Decorator for timing operations"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self.start_timer(operation_name)
                try:
                    result = await func(*args, **kwargs)
                    self.end_timer(operation_name, {'success': True})
                    return result
                except Exception as e:
                    self.end_timer(operation_name, {'success': False, 'error': str(e)})
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                self.start_timer(operation_name)
                try:
                    result = func(*args, **kwargs)
                    self.end_timer(operation_name, {'success': True})
                    return result
                except Exception as e:
                    self.end_timer(operation_name, {'success': False, 'error': str(e)})
                    raise
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator

    def track_cache_performance(self, hit: bool):
        """Track cache hit/miss performance"""
        if hit:
            self.performance_metrics['cache_hits'] += 1
        else:
            self.performance_metrics['cache_misses'] += 1

        # Calculate cache effectiveness
        total_requests = self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']
        if total_requests > 0:
            self.performance_metrics['cache_effectiveness'] = self.performance_metrics['cache_hits'] / total_requests

    def track_api_call(self, endpoint: str, response_time: float, success: bool = True):
        """Track API call performance"""
        self.performance_metrics['api_calls'] += 1

        if self.alerts_enabled and self.check_metrics:
            metrics = {
                'api_call_time': response_time,
                'endpoint': endpoint,
                'success': success
            }
            self.check_metrics(metrics)

    def track_concurrent_operation(self, operation_type: str, task_count: int = 1):
        """Track concurrent operations"""
        self.performance_metrics['concurrent_operations'] += 1
        self.performance_metrics['concurrent_tasks_active'] += task_count

    def update_system_metrics(self):
        """Update system resource metrics"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent(interval=0.1)

                # Keep last 100 readings
                self.performance_metrics['memory_usage'].append(memory_mb)
                self.performance_metrics['cpu_usage'].append(cpu_percent)

                if len(self.performance_metrics['memory_usage']) > 100:
                    self.performance_metrics['memory_usage'] = self.performance_metrics['memory_usage'][-100:]
                if len(self.performance_metrics['cpu_usage']) > 100:
                    self.performance_metrics['cpu_usage'] = self.performance_metrics['cpu_usage'][-100:]

                # Calculate averages
                if self.performance_metrics['memory_usage']:
                    avg_memory = sum(self.performance_metrics['memory_usage']) / len(self.performance_metrics['memory_usage'])
                    self.performance_metrics['avg_memory_mb'] = avg_memory

                if self.performance_metrics['cpu_usage']:
                    avg_cpu = sum(self.performance_metrics['cpu_usage']) / len(self.performance_metrics['cpu_usage'])
                    self.performance_metrics['avg_cpu_percent'] = avg_cpu

            except Exception as e:
                self.logger.log_error(e, {'context': 'system_metrics_update'})

    def track_performance_mode_usage(self, component: str, enabled: bool):
        """Track which components are using performance mode"""
        self.performance_metrics['optimization_usage'][component] = {
            'performance_mode': enabled,
            'timestamp': datetime.now().isoformat()
        }

        # Update overall performance mode status
        perf_mode_components = sum(1 for comp in self.performance_metrics['optimization_usage'].values()
                                 if comp.get('performance_mode', False))
        total_components = len(self.performance_metrics['optimization_usage'])
        self.performance_metrics['performance_mode_enabled'] = perf_mode_components > 0

    def check_optimization_effectiveness(self) -> Dict:
        """Check if performance optimizations are effective"""
        results = {
            'cache_effective': self.performance_metrics['cache_effectiveness'] > 0.7,
            'memory_optimized': self.performance_metrics.get('avg_memory_mb', 0) < 500,
            'concurrent_active': self.performance_metrics['concurrent_tasks_active'] > 0,
            'performance_mode_active': self.performance_metrics['performance_mode_enabled'],
            'overall_score': 0.0
        }

        # Calculate overall optimization score
        scores = [
            results['cache_effective'],
            results['memory_optimized'],
            results['concurrent_active'],
            results['performance_mode_active']
        ]
        results['overall_score'] = sum(scores) / len(scores)

        return results

    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        self.update_system_metrics()

        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_performance': {
                'hits': self.performance_metrics['cache_hits'],
                'misses': self.performance_metrics['cache_misses'],
                'effectiveness': self.performance_metrics['cache_effectiveness']
            },
            'system_resources': {
                'avg_memory_mb': self.performance_metrics.get('avg_memory_mb', 0),
                'avg_cpu_percent': self.performance_metrics.get('avg_cpu_percent', 0),
                'current_memory_mb': self.performance_metrics['memory_usage'][-1] if self.performance_metrics['memory_usage'] else 0,
                'current_cpu_percent': self.performance_metrics['cpu_usage'][-1] if self.performance_metrics['cpu_usage'] else 0
            },
            'optimization_status': {
                'performance_mode_enabled': self.performance_metrics['performance_mode_enabled'],
                'concurrent_operations': self.performance_metrics['concurrent_operations'],
                'active_tasks': self.performance_metrics['concurrent_tasks_active'],
                'memory_optimization': self.performance_metrics['memory_optimization_active']
            },
            'api_performance': {
                'total_calls': self.performance_metrics['api_calls']
            },
            'optimization_effectiveness': self.check_optimization_effectiveness()
        }

        return report


class HealthChecker:
    """Health check system for monitoring bot status"""
    
    def __init__(self, logger: ProductionLogger):
        self.logger = logger
        self.health_status = {
            'status': 'healthy',
            'last_check': None,
            'checks': {},
            'performance_checks': {}
        }
    
    def check_database(self, db_manager) -> bool:
        """Check database connectivity"""
        try:
            session = db_manager.get_session()
            session.execute("SELECT 1")
            session.close()
            self.health_status['checks']['database'] = 'healthy'
            return True
        except Exception as e:
            self.health_status['checks']['database'] = f'unhealthy: {e}'
            self.logger.log_error(e, {'check': 'database'})
            return False
    
    def check_telegram_api(self, bot_token: str) -> bool:
        """Check Telegram API connectivity"""
        try:
            import requests
            response = requests.get(
                f'https://api.telegram.org/bot{bot_token}/getMe',
                timeout=5
            )
            if response.status_code == 200:
                self.health_status['checks']['telegram'] = 'healthy'
                return True
            else:
                self.health_status['checks']['telegram'] = 'unhealthy'
                return False
        except Exception as e:
            self.health_status['checks']['telegram'] = f'unhealthy: {e}'
            return False
    
    def check_disk_space(self, min_gb: float = 1.0) -> bool:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free / (1024**3)
            
            if free_gb >= min_gb:
                self.health_status['checks']['disk_space'] = f'healthy ({free_gb:.2f} GB free)'
                return True
            else:
                self.health_status['checks']['disk_space'] = f'low ({free_gb:.2f} GB free)'
                return False
        except Exception as e:
            self.health_status['checks']['disk_space'] = f'error: {e}'
            return False
    
    def run_all_checks(self, db_manager=None, bot_token=None) -> Dict:
        """Run all health checks"""
        self.health_status['last_check'] = datetime.now().isoformat()
        
        if db_manager:
            self.check_database(db_manager)
        
        if bot_token:
            self.check_telegram_api(bot_token)
        
        self.check_disk_space()
        
        # Determine overall status
        all_healthy = all(
            'healthy' in status or 'GB free' in status
            for status in self.health_status['checks'].values()
        )
        
        self.health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        # Performance-specific health checks
        self.check_performance_optimizations()
        self.check_memory_health()
        self.check_cache_health()

        return self.health_status

    def check_performance_optimizations(self):
        """Check performance optimization status"""
        try:
            import config
            perf_mode = getattr(config, 'PERFORMANCE_MODE', False)

            if perf_mode:
                self.health_status['performance_checks']['performance_mode'] = 'enabled'
            else:
                self.health_status['performance_checks']['performance_mode'] = 'disabled'
                self.logger.log_error(Exception("Performance mode disabled in production"),
                                    {'check': 'performance_optimizations'})

        except Exception as e:
            self.health_status['performance_checks']['performance_mode'] = f'error: {e}'

    def check_memory_health(self):
        """Check memory optimization health"""
        try:
            import memory_optimizer
            optimizer = memory_optimizer.get_optimizer()
            stats = optimizer.get_memory_stats()

            current_memory = stats.get('current_memory_mb', 0)
            threshold = stats.get('memory_threshold_mb', 500)

            if current_memory > threshold:
                self.health_status['performance_checks']['memory_usage'] = f'unhealthy ({current_memory:.1f}MB > {threshold}MB)'
                self.logger.log_error(Exception(f"Memory usage exceeded threshold: {current_memory:.1f}MB"),
                                    {'check': 'memory_health'})
            else:
                self.health_status['performance_checks']['memory_usage'] = f'healthy ({current_memory:.1f}MB)'

        except Exception as e:
            self.health_status['performance_checks']['memory_usage'] = f'error: {e}'

    def check_cache_health(self):
        """Check cache system health"""
        try:
            from data_fetcher import BinanceDataFetcher
            fetcher = BinanceDataFetcher(performance_mode=True)

            if hasattr(fetcher, 'cache'):
                cache_size = len(fetcher.cache) if fetcher.cache else 0
                self.health_status['performance_checks']['cache_system'] = f'healthy ({cache_size} entries)'
            else:
                self.health_status['performance_checks']['cache_system'] = 'not_available'
                self.logger.log_error(Exception("Cache system not available"),
                                    {'check': 'cache_health'})

        except Exception as e:
            self.health_status['performance_checks']['cache_system'] = f'error: {e}'


# Global instances
_logger = None
_perf_monitor = None
_health_checker = None

def get_logger() -> ProductionLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = ProductionLogger()
    return _logger

def get_perf_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    global _perf_monitor
    if _perf_monitor is None:
        _perf_monitor = PerformanceMonitor(get_logger())
    return _perf_monitor

def get_health_checker() -> HealthChecker:
    """Get global health checker"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(get_logger())
    return _health_checker

