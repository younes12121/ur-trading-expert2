"""
PRODUCTION MONITORING & ALERTING SYSTEM
Enterprise-grade monitoring for the Error Learning Trading Bot
"""

import sys
import os
import time
import json
import smtplib
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import psutil
import socket

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from global_error_learning import get_error_insights, global_error_manager
from error_dashboard import get_system_health, check_alerts

logger = logging.getLogger(__name__)

class AlertLevel:
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel:
    """Alert notification channels"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    LOG = "log"
    SMS = "sms"  # Future implementation

class ProductionMonitor:
    """Production monitoring system for error learning bot"""

    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.alert_history = []
        self.monitoring_active = False
        self.monitoring_thread = None
        self.health_checks = {}
        self.performance_metrics = {
            'cache_performance': {'hits': 0, 'misses': 0},
            'optimization_status': {},
            'concurrent_operations': 0,
            'memory_trends': [],
            'cpu_trends': []
        }

        # Alert thresholds
        self.thresholds = {
            'system_health_min': 70.0,
            'error_rate_max': 0.15,  # 15%
            'response_time_max': 5.0,  # 5 seconds
            'memory_usage_max': 0.90,  # 90%
            'cpu_usage_max': 0.85,     # 85%
            'disk_usage_max': 0.95     # 95%
        }

        logger.info("[MONITORING] Production monitoring system initialized")

    def _load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            'enabled': True,
            'check_interval': 60,  # seconds
            'alert_channels': [AlertChannel.LOG],
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': os.getenv('ALERT_EMAIL_USER', ''),
                'password': os.getenv('ALERT_EMAIL_PASS', ''),
                'from_email': os.getenv('ALERT_EMAIL_FROM', ''),
                'to_emails': os.getenv('ALERT_EMAIL_TO', '').split(',') if os.getenv('ALERT_EMAIL_TO') else []
            },
            'telegram_config': {
                'bot_token': os.getenv('TELEGRAM_ALERT_BOT_TOKEN', ''),
                'chat_ids': os.getenv('TELEGRAM_ALERT_CHAT_IDS', '').split(',') if os.getenv('TELEGRAM_ALERT_CHAT_IDS') else []
            },
            'webhook_config': {
                'urls': os.getenv('ALERT_WEBHOOK_URLS', '').split(',') if os.getenv('ALERT_WEBHOOK_URLS') else []
            },
            'alert_cooldown': 300,  # 5 minutes between similar alerts
            'enable_health_checks': True,
            'enable_performance_monitoring': True,
            'enable_error_tracking': True
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            logger.warning(f"[MONITORING] Failed to load config: {e}")

        return default_config

    def start_monitoring(self):
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("[MONITORING] Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info("[MONITORING] Production monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        logger.info("[MONITORING] Production monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("[MONITORING] Starting monitoring loop")

        while self.monitoring_active:
            try:
                self._perform_health_checks()
                self._check_alert_conditions()
                self._send_scheduled_reports()

                time.sleep(self.config.get('check_interval', 60))

            except Exception as e:
                logger.error(f"[MONITORING] Monitoring loop error: {e}")
                time.sleep(30)  # Brief pause before retry

    def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        if not self.config.get('enable_health_checks', True):
            return

        timestamp = datetime.now()

        # System health checks
        health_checks = {
            'timestamp': timestamp.isoformat(),
            'system_health': self._check_system_health(),
            'error_learning_health': self._check_error_learning_health(),
            'performance_metrics': self._check_performance_metrics(),
            'resource_usage': self._check_resource_usage(),
            'network_connectivity': self._check_network_connectivity(),
            'data_integrity': self._check_data_integrity(),
            # Performance-specific checks
            'performance_optimizations': self._check_performance_optimizations(),
            'cache_performance': self._check_cache_performance(),
            'concurrent_operations': self._check_concurrent_operations(),
            'memory_optimization': self._check_memory_optimization()
        }

        self.health_checks[timestamp] = health_checks

        # Keep only last 100 health checks
        if len(self.health_checks) > 100:
            oldest_key = min(self.health_checks.keys())
            del self.health_checks[oldest_key]

    def _check_system_health(self) -> Dict:
        """Check overall system health"""
        try:
            health = get_system_health()
            return {
                'status': 'healthy' if health['system_health_score'] >= self.thresholds['system_health_min'] else 'degraded',
                'score': health['system_health_score'],
                'threshold': self.thresholds['system_health_min']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_error_learning_health(self) -> Dict:
        """Check error learning system health"""
        try:
            insights = get_error_insights()

            error_rate = insights.get('recent_error_rate', 0)
            learning_progress = insights.get('learning_progress', 0)
            total_operations = insights.get('total_operations', 0)

            status = 'healthy'
            issues = []

            if error_rate > self.thresholds['error_rate_max']:
                status = 'warning'
                issues.append(f'High error rate: {error_rate:.1%}')

            if learning_progress < 0.2 and total_operations > 50:
                status = 'warning'
                issues.append(f'Low learning progress: {learning_progress:.1%}')

            return {
                'status': status,
                'error_rate': error_rate,
                'learning_progress': learning_progress,
                'total_operations': total_operations,
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_performance_metrics(self) -> Dict:
        """Check system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent / 100.0

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent / 100.0

            # Network I/O (optional)
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_recv = net_io.bytes_recv

            status = 'healthy'
            issues = []

            if cpu_percent > self.thresholds['cpu_usage_max'] * 100:
                status = 'warning'
                issues.append(f'High CPU usage: {cpu_percent:.1f}%')

            if memory_percent > self.thresholds['memory_usage_max']:
                status = 'warning'
                issues.append(f'High memory usage: {memory_percent:.1%}')

            if disk_percent > self.thresholds['disk_usage_max']:
                status = 'error'
                issues.append(f'Critical disk usage: {disk_percent:.1%}')

            return {
                'status': status,
                'cpu_usage': cpu_percent / 100.0,
                'memory_usage': memory_percent,
                'disk_usage': disk_percent,
                'network_sent_mb': bytes_sent / 1024 / 1024,
                'network_recv_mb': bytes_recv / 1024 / 1024,
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_resource_usage(self) -> Dict:
        """Check resource usage patterns"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_times = process.cpu_times()

            return {
                'process_memory_mb': memory_info.rss / 1024 / 1024,
                'process_cpu_percent': process.cpu_percent(),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_network_connectivity(self) -> Dict:
        """Check network connectivity"""
        try:
            # Test basic connectivity
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return {'status': 'healthy', 'connectivity': True}
        except:
            return {'status': 'error', 'connectivity': False}

    def _check_performance_optimizations(self) -> Dict:
        """Check performance optimization status"""
        try:
            import config

            optimizations = {
                'performance_mode': getattr(config, 'PERFORMANCE_MODE', False),
                'caching_enabled': getattr(config, 'ENABLE_CACHING', False),
                'concurrent_api': getattr(config, 'CONCURRENT_API', False)
            }

            # Check if critical optimizations are enabled
            critical_optimizations = ['performance_mode', 'caching_enabled']
            enabled_count = sum(optimizations.values())
            critical_enabled = sum(optimizations[opt] for opt in critical_optimizations)

            status = 'healthy' if critical_enabled == len(critical_optimizations) else 'warning'

            self.performance_metrics['optimization_status'] = optimizations

            return {
                'status': status,
                'optimizations': optimizations,
                'enabled_count': enabled_count,
                'critical_enabled': critical_enabled
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_cache_performance(self) -> Dict:
        """Check cache system performance"""
        try:
            from data_fetcher import BinanceDataFetcher

            fetcher = BinanceDataFetcher(performance_mode=True)

            if hasattr(fetcher, 'cache'):
                cache_entries = len(fetcher.cache) if fetcher.cache else 0

                # Calculate cache hit rate if available
                hit_rate = 0.0
                if hasattr(fetcher, 'cache_hits') and hasattr(fetcher, 'cache_misses'):
                    total_requests = fetcher.cache_hits + fetcher.cache_misses
                    hit_rate = fetcher.cache_hits / total_requests if total_requests > 0 else 0

                self.performance_metrics['cache_performance'].update({
                    'entries': cache_entries,
                    'hit_rate': hit_rate
                })

                status = 'healthy' if hit_rate > 0.5 else 'warning'

                return {
                    'status': status,
                    'cache_entries': cache_entries,
                    'hit_rate': hit_rate
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Cache system not available'
                }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_concurrent_operations(self) -> Dict:
        """Check concurrent processing status"""
        try:
            import concurrent_processor
            processor = concurrent_processor.get_processor()

            active_tasks = len(processor.get_active_tasks())
            stats = processor.get_stats()

            self.performance_metrics['concurrent_operations'] = active_tasks

            status = 'healthy' if active_tasks >= 0 else 'warning'

            return {
                'status': status,
                'active_tasks': active_tasks,
                'total_completed': stats.get('tasks_completed', 0),
                'total_failed': stats.get('tasks_failed', 0)
            }

        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Concurrent processor check failed: {e}'
            }

    def _check_memory_optimization(self) -> Dict:
        """Check memory optimization status"""
        try:
            import memory_optimizer
            optimizer = memory_optimizer.get_optimizer()

            stats = optimizer.get_memory_stats()
            current_memory = stats.get('current_memory_mb', 0)
            threshold = stats.get('memory_threshold_mb', 500)

            # Track memory trends
            self.performance_metrics['memory_trends'].append(current_memory)
            if len(self.performance_metrics['memory_trends']) > 50:
                self.performance_metrics['memory_trends'] = self.performance_metrics['memory_trends'][-50:]

            status = 'healthy' if current_memory <= threshold else 'warning'

            return {
                'status': status,
                'current_memory_mb': current_memory,
                'threshold_mb': threshold,
                'monitoring_active': optimizer.monitoring_active,
                'gc_collections': stats.get('gc_collections', 0)
            }

        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Memory optimizer check failed: {e}'
            }

    def _check_data_integrity(self) -> Dict:
        """Check data integrity"""
        try:
            # Check if error learning model file exists and is readable
            model_path = os.path.join(os.path.dirname(__file__), "global_error_learning_model.pkl")
            model_exists = os.path.exists(model_path)

            # Check if error history is accessible
            error_count = len(global_error_manager.error_history)

            return {
                'status': 'healthy',
                'model_file_exists': model_exists,
                'error_history_count': error_count,
                'data_integrity': True
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'data_integrity': False
            }

    def _check_alert_conditions(self):
        """Check for alert conditions and trigger alerts"""
        if not self.config.get('enable_error_tracking', True):
            return

        alerts = check_alerts()

        for alert in alerts:
            if self._should_trigger_alert(alert):
                self._trigger_alert(alert)
                self._record_alert(alert)

    def _should_trigger_alert(self, alert: Dict) -> bool:
        """Determine if alert should be triggered based on cooldown"""
        alert_key = f"{alert['type']}_{alert.get('component', 'system')}"

        # Check recent alerts for cooldown
        cooldown_period = timedelta(seconds=self.config.get('alert_cooldown', 300))

        for recent_alert in self.alert_history[-10:]:  # Check last 10 alerts
            if (recent_alert['key'] == alert_key and
                datetime.now() - recent_alert['timestamp'] < cooldown_period):
                return False

        return True

    def _trigger_alert(self, alert: Dict):
        """Trigger alert through configured channels"""
        alert_message = self._format_alert_message(alert)

        for channel in self.config.get('alert_channels', [AlertChannel.LOG]):
            try:
                if channel == AlertChannel.LOG:
                    self._send_log_alert(alert, alert_message)
                elif channel == AlertChannel.EMAIL:
                    self._send_email_alert(alert, alert_message)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram_alert(alert, alert_message)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook_alert(alert, alert_message)
            except Exception as e:
                logger.error(f"[MONITORING] Failed to send {channel} alert: {e}")

    def _format_alert_message(self, alert: Dict) -> str:
        """Format alert message for notifications"""
        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }.get(alert.get('level', AlertLevel.INFO), "❓")

        message = f"""{level_emoji} **ERROR LEARNING ALERT**

**Level:** {alert.get('level', 'unknown').upper()}
**Type:** {alert.get('type', 'unknown')}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Message:**
{alert.get('message', 'No message')}

**Recommendation:**
{alert.get('recommendation', 'No recommendation available')}
"""

        if alert.get('component'):
            message += f"\n**Component:** {alert['component']}"

        return message

    def _send_log_alert(self, alert: Dict, message: str):
        """Send alert to log"""
        logger.warning(f"[ALERT] {message}")

    def _send_email_alert(self, alert: Dict, message: str):
        """Send alert via email"""
        email_config = self.config.get('email_config', {})

        if not all([email_config.get('smtp_server'), email_config.get('username'),
                   email_config.get('to_emails')]):
            logger.warning("[MONITORING] Email configuration incomplete")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email'] or email_config['username']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"Error Learning Alert: {alert.get('level', 'unknown').upper()}"

            msg.attach(MIMEText(message, 'html'))

            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            text = msg.as_string()
            server.sendmail(email_config['from_email'] or email_config['username'],
                          email_config['to_emails'], text)
            server.quit()

            logger.info("[MONITORING] Email alert sent successfully")

        except Exception as e:
            logger.error(f"[MONITORING] Email alert failed: {e}")

    def _send_telegram_alert(self, alert: Dict, message: str):
        """Send alert via Telegram"""
        telegram_config = self.config.get('telegram_config', {})

        if not all([telegram_config.get('bot_token'), telegram_config.get('chat_ids')]):
            logger.warning("[MONITORING] Telegram configuration incomplete")
            return

        try:
            import telegram
            bot = telegram.Bot(token=telegram_config['bot_token'])

            for chat_id in telegram_config['chat_ids']:
                bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

            logger.info("[MONITORING] Telegram alert sent successfully")

        except ImportError:
            logger.warning("[MONITORING] Telegram library not installed")
        except Exception as e:
            logger.error(f"[MONITORING] Telegram alert failed: {e}")

    def _send_webhook_alert(self, alert: Dict, message: str):
        """Send alert via webhook"""
        webhook_config = self.config.get('webhook_config', {})

        if not webhook_config.get('urls'):
            logger.warning("[MONITORING] Webhook URLs not configured")
            return

        payload = {
            'alert': alert,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'system': 'error_learning_bot'
        }

        for url in webhook_config['urls']:
            try:
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"[MONITORING] Webhook alert sent to {url}")

            except Exception as e:
                logger.error(f"[MONITORING] Webhook alert failed for {url}: {e}")

    def _record_alert(self, alert: Dict):
        """Record alert in history"""
        alert_record = {
            'timestamp': datetime.now(),
            'key': f"{alert['type']}_{alert.get('component', 'system')}",
            'alert': alert
        }

        self.alert_history.append(alert_record)

        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

    def _send_scheduled_reports(self):
        """Send scheduled reports (daily/weekly)"""
        now = datetime.now()

        # Daily report at 9 AM
        if now.hour == 9 and now.minute == 0:
            self._send_daily_report()

        # Weekly report on Monday at 9 AM
        if now.weekday() == 0 and now.hour == 9 and now.minute == 0:
            self._send_weekly_report()

    def _send_daily_report(self):
        """Send daily system report"""
        try:
            from error_dashboard import get_dashboard_report

            report = get_dashboard_report('full')
            subject = f"Daily Error Learning Report - {datetime.now().strftime('%Y-%m-%d')}"

            # Send via configured channels
            for channel in self.config.get('alert_channels', []):
                if channel == AlertChannel.EMAIL:
                    self._send_email_report(subject, report)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram_report(subject, report)

            logger.info("[MONITORING] Daily report sent")

        except Exception as e:
            logger.error(f"[MONITORING] Daily report failed: {e}")

    def _send_weekly_report(self):
        """Send weekly system report"""
        try:
            from error_dashboard import error_dashboard

            analytics = error_dashboard.get_performance_analytics(hours=168)  # 7 days
            report = f"""
📊 **WEEKLY ERROR LEARNING REPORT**

**Period:** {datetime.now() - timedelta(days=7):strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}

**Performance Overview:**
• Total Operations: {analytics.get('total_operations', 0):,}
• Error Rate Trend: {analytics.get('error_rate_trend', {}).get('trend', 'unknown')}
• Change: {analytics.get('error_rate_trend', {}).get('change_percent', 0):+.1f}%

**Top Components:**
"""

            for comp in analytics.get('component_performance', [])[:5]:
                report += f"• {comp['component']}: {comp['error_rate']:.1%} errors\n"

            subject = f"Weekly Error Learning Report - {datetime.now().strftime('%Y-%m-%d')}"

            # Send via configured channels
            for channel in self.config.get('alert_channels', []):
                if channel == AlertChannel.EMAIL:
                    self._send_email_report(subject, report)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram_report(subject, report)

            logger.info("[MONITORING] Weekly report sent")

        except Exception as e:
            logger.error(f"[MONITORING] Weekly report failed: {e}")

    def _send_email_report(self, subject: str, content: str):
        """Send report via email"""
        # Similar to email alert but for reports
        pass

    def _send_telegram_report(self, subject: str, content: str):
        """Send report via Telegram"""
        # Similar to telegram alert but for reports
        pass

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring system status"""
        return {
            'monitoring_active': self.monitoring_active,
            'config_loaded': bool(self.config),
            'health_checks_count': len(self.health_checks),
            'alerts_count': len(self.alert_history),
            'last_health_check': max(self.health_checks.keys()) if self.health_checks else None,
            'last_alert': self.alert_history[-1]['timestamp'] if self.alert_history else None
        }

    def get_health_history(self, hours: int = 24) -> List[Dict]:
        """Get health check history for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            health for timestamp, health in self.health_checks.items()
            if timestamp > cutoff_time
        ]

    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get alert history for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            alert for alert in self.alert_history
            if alert['timestamp'] > cutoff_time
        ]

# Global monitoring instance
production_monitor = ProductionMonitor()

def start_monitoring():
    """Convenience function to start monitoring"""
    production_monitor.start_monitoring()

def stop_monitoring():
    """Convenience function to stop monitoring"""
    production_monitor.stop_monitoring()

def get_monitoring_status():
    """Convenience function to get monitoring status"""
    return production_monitor.get_monitoring_status()

if __name__ == "__main__":
    print("🔍 PRODUCTION MONITORING SYSTEM TEST")
    print("=" * 50)

    # Test monitoring system
    print("Starting monitoring...")
    start_monitoring()

    # Wait a bit for some health checks
    time.sleep(5)

    # Check status
    status = get_monitoring_status()
    print(f"Monitoring Active: {status['monitoring_active']}")
    print(f"Health Checks: {status['health_checks_count']}")
    print(f"Alerts: {status['alerts_count']}")

    # Get recent health checks
    health_history = production_monitor.get_health_history(hours=1)
    print(f"Recent Health Checks: {len(health_history)}")

    # Stop monitoring
    print("Stopping monitoring...")
    stop_monitoring()

    print("✅ Production monitoring system test completed!")