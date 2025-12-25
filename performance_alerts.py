"""
Performance Alerting System
Monitors performance metrics and sends alerts when thresholds are exceeded
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum
import json

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertChannel:
    """Alert delivery channel"""
    CONSOLE = "console"
    LOG_FILE = "log_file"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"

class PerformanceAlerts:
    """Performance monitoring and alerting system"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logger()
        self.alert_history = []
        self.metrics_history = []
        self.alert_callbacks = {
            AlertChannel.CONSOLE: self._console_alert,
            AlertChannel.LOG_FILE: self._log_file_alert
        }
        
    def _default_config(self) -> Dict:
        """Default alert configuration"""
        return {
            'performance_degradation_threshold': 0.20,  # 20% slower
            'memory_usage_threshold': 0.80,  # 80% memory
            'error_rate_threshold': 0.05,  # 5% errors
            'api_rate_limit_threshold': 0.80,  # 80% of limit
            'cache_miss_rate_threshold': 0.50,  # 50% miss rate
            'cpu_usage_threshold': 0.80,  # 80% CPU
            'channels': [AlertChannel.CONSOLE, AlertChannel.LOG_FILE]
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('performance_alerts')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('performance_alerts.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_performance_degradation(self, current_time: float, baseline_time: float) -> bool:
        """Check if performance has degraded"""
        if baseline_time == 0:
            return False
        
        degradation = (current_time - baseline_time) / baseline_time
        threshold = self.config['performance_degradation_threshold']
        
        if degradation > threshold:
            self.send_alert(
                AlertLevel.WARNING,
                "Performance Degradation",
                f"Execution time increased by {degradation*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'current_time': current_time, 'baseline_time': baseline_time, 'degradation': degradation}
            )
            return True
        return False
    
    def check_memory_usage(self, memory_percent: float) -> bool:
        """Check memory usage"""
        threshold = self.config['memory_usage_threshold']
        
        if memory_percent > threshold:
            level = AlertLevel.CRITICAL if memory_percent > 0.90 else AlertLevel.WARNING
            self.send_alert(
                level,
                "High Memory Usage",
                f"Memory usage at {memory_percent*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'memory_percent': memory_percent}
            )
            return True
        return False
    
    def check_error_rate(self, error_rate: float) -> bool:
        """Check error rate"""
        threshold = self.config['error_rate_threshold']
        
        if error_rate > threshold:
            level = AlertLevel.CRITICAL if error_rate > 0.10 else AlertLevel.WARNING
            self.send_alert(
                level,
                "High Error Rate",
                f"Error rate at {error_rate*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'error_rate': error_rate}
            )
            return True
        return False
    
    def check_api_rate_limit(self, usage_percent: float) -> bool:
        """Check API rate limit usage"""
        threshold = self.config['api_rate_limit_threshold']
        
        if usage_percent > threshold:
            self.send_alert(
                AlertLevel.WARNING,
                "API Rate Limit Warning",
                f"API rate limit usage at {usage_percent*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'usage_percent': usage_percent}
            )
            return True
        return False
    
    def check_cache_miss_rate(self, miss_rate: float) -> bool:
        """Check cache miss rate"""
        threshold = self.config['cache_miss_rate_threshold']
        
        if miss_rate > threshold:
            self.send_alert(
                AlertLevel.WARNING,
                "High Cache Miss Rate",
                f"Cache miss rate at {miss_rate*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'miss_rate': miss_rate}
            )
            return True
        return False
    
    def check_cpu_usage(self, cpu_percent: float) -> bool:
        """Check CPU usage"""
        threshold = self.config['cpu_usage_threshold']
        
        if cpu_percent > threshold:
            level = AlertLevel.CRITICAL if cpu_percent > 0.90 else AlertLevel.WARNING
            self.send_alert(
                level,
                "High CPU Usage",
                f"CPU usage at {cpu_percent*100:.1f}% (threshold: {threshold*100:.1f}%)",
                {'cpu_percent': cpu_percent}
            )
            return True
        return False
    
    def send_alert(self, level: AlertLevel, title: str, message: str, metadata: Optional[Dict] = None):
        """Send alert through configured channels"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level.value,
            'title': title,
            'message': message,
            'metadata': metadata or {}
        }
        
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Send through configured channels
        for channel in self.config.get('channels', []):
            if channel in self.alert_callbacks:
                try:
                    self.alert_callbacks[channel](alert)
                except Exception as e:
                    self.logger.error(f"Failed to send alert via {channel}: {e}")
    
    def _console_alert(self, alert: Dict):
        """Send alert to console"""
        level_symbol = {
            'info': 'ℹ',
            'warning': '⚠',
            'critical': '🚨'
        }.get(alert['level'], '•')
        
        print(f"\n{level_symbol} ALERT [{alert['level'].upper()}] {alert['title']}")
        print(f"   {alert['message']}")
        if alert['metadata']:
            print(f"   Metadata: {json.dumps(alert['metadata'], indent=2)}")
        print()
    
    def _log_file_alert(self, alert: Dict):
        """Send alert to log file"""
        self.logger.warning(f"{alert['title']}: {alert['message']}")
        if alert['metadata']:
            self.logger.debug(f"Metadata: {json.dumps(alert['metadata'])}")
    
    def register_callback(self, channel: AlertChannel, callback: Callable):
        """Register custom alert callback"""
        self.alert_callbacks[channel] = callback
    
    def get_alert_history(self, level: Optional[AlertLevel] = None, limit: int = 100) -> List[Dict]:
        """Get alert history"""
        alerts = self.alert_history
        
        if level:
            alerts = [a for a in alerts if a['level'] == level.value]
        
        return alerts[-limit:]
    
    def get_alert_summary(self) -> Dict:
        """Get alert summary statistics"""
        total = len(self.alert_history)
        by_level = {}
        
        for alert in self.alert_history:
            level = alert['level']
            by_level[level] = by_level.get(level, 0) + 1
        
        return {
            'total_alerts': total,
            'by_level': by_level,
            'recent_alerts': self.get_alert_history(limit=10)
        }

# Global alert instance
_global_alerts = None

def get_alerts() -> PerformanceAlerts:
    """Get global alerts instance"""
    global _global_alerts
    if _global_alerts is None:
        _global_alerts = PerformanceAlerts()
    return _global_alerts

def check_performance_metrics(metrics: Dict):
    """Check performance metrics and send alerts if needed"""
    alerts = get_alerts()
    
    # Check various metrics
    if 'execution_time' in metrics and 'baseline_time' in metrics:
        alerts.check_performance_degradation(
            metrics['execution_time'],
            metrics['baseline_time']
        )
    
    if 'memory_percent' in metrics:
        alerts.check_memory_usage(metrics['memory_percent'])
    
    if 'error_rate' in metrics:
        alerts.check_error_rate(metrics['error_rate'])
    
    if 'api_usage_percent' in metrics:
        alerts.check_api_rate_limit(metrics['api_usage_percent'])
    
    if 'cache_miss_rate' in metrics:
        alerts.check_cache_miss_rate(metrics['cache_miss_rate'])
    
    if 'cpu_percent' in metrics:
        alerts.check_cpu_usage(metrics['cpu_percent'])

def main():
    """Test the alerting system"""
    print("="*60)
    print("PERFORMANCE ALERTING SYSTEM TEST")
    print("="*60)
    
    alerts = PerformanceAlerts()
    
    # Test various alerts
    print("\nTesting alerts...")
    
    alerts.check_performance_degradation(1.5, 1.0)  # 50% degradation
    alerts.check_memory_usage(0.85)  # 85% memory
    alerts.check_error_rate(0.06)  # 6% error rate
    alerts.check_api_rate_limit(0.85)  # 85% API usage
    alerts.check_cache_miss_rate(0.55)  # 55% miss rate
    alerts.check_cpu_usage(0.85)  # 85% CPU
    
    # Show summary
    summary = alerts.get_alert_summary()
    print(f"\nAlert Summary:")
    print(f"  Total alerts: {summary['total_alerts']}")
    print(f"  By level: {summary['by_level']}")
    
    print("\nRecent alerts:")
    for alert in summary['recent_alerts'][-5:]:
        print(f"  [{alert['level']}] {alert['title']}: {alert['message']}")

if __name__ == "__main__":
    main()
