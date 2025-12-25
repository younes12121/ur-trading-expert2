#!/usr/bin/env python3
"""
Feature Monitoring System
Monitors usage and performance of premium features
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class FeatureMonitor:
    """Monitor premium feature usage and performance"""

    def __init__(self, data_file="feature_monitoring.json"):
        self.data_file = data_file
        self.monitoring_data = {
            'features': {},
            'performance': {},
            'errors': {},
            'usage_stats': {},
            'premium_metrics': {}
        }
        self.load_data()

        # Configure logging
        self.logger = logging.getLogger('feature_monitor')
        self.logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # File handler for feature monitoring
        fh = logging.FileHandler('logs/feature_monitoring.log')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def load_data(self):
        """Load monitoring data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.monitoring_data = json.load(f)
            except Exception as e:
                print(f"Error loading monitoring data: {e}")
                self.monitoring_data = self._get_default_data()

    def save_data(self):
        """Save monitoring data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving monitoring data: {e}")

    def _get_default_data(self):
        """Get default monitoring data structure"""
        return {
            'features': {},
            'performance': {},
            'errors': {},
            'usage_stats': {},
            'premium_metrics': {}
        }

    # ============================================================================
    # FEATURE USAGE TRACKING
    # ============================================================================

    def track_feature_usage(self, feature_name: str, user_id: int, user_tier: str,
                          success: bool, execution_time: float, metadata: Dict = None):
        """Track usage of a specific feature"""

        timestamp = datetime.now().isoformat()

        # Initialize feature data if not exists
        if feature_name not in self.monitoring_data['features']:
            self.monitoring_data['features'][feature_name] = {
                'total_uses': 0,
                'successful_uses': 0,
                'failed_uses': 0,
                'avg_execution_time': 0,
                'tier_breakdown': {'free': 0, 'premium': 0, 'vip': 0},
                'daily_usage': {},
                'last_used': None
            }

        feature_data = self.monitoring_data['features'][feature_name]

        # Update counters
        feature_data['total_uses'] += 1
        feature_data['tier_breakdown'][user_tier] += 1
        feature_data['last_used'] = timestamp

        if success:
            feature_data['successful_uses'] += 1
        else:
            feature_data['failed_uses'] += 1

        # Update average execution time
        current_avg = feature_data['avg_execution_time']
        total_uses = feature_data['total_uses']
        feature_data['avg_execution_time'] = (current_avg * (total_uses - 1) + execution_time) / total_uses

        # Daily usage tracking
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in feature_data['daily_usage']:
            feature_data['daily_usage'][today] = 0
        feature_data['daily_usage'][today] += 1

        # Log the usage
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"FEATURE_USAGE: {feature_name} | User: {user_id} | Tier: {user_tier} | {status} | Time: {execution_time:.2f}s")

        if metadata:
            self.logger.info(f"FEATURE_METADATA: {feature_name} | {json.dumps(metadata)}")

        self.save_data()

    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================

    def track_performance(self, operation: str, execution_time: float, success: bool,
                         metadata: Dict = None):
        """Track performance metrics for operations"""

        timestamp = datetime.now().isoformat()

        if operation not in self.monitoring_data['performance']:
            self.monitoring_data['performance'][operation] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'avg_execution_time': 0,
                'min_execution_time': float('inf'),
                'max_execution_time': 0,
                'last_executed': None,
                'performance_history': []
            }

        perf_data = self.monitoring_data['performance'][operation]

        perf_data['total_calls'] += 1
        perf_data['last_executed'] = timestamp

        if success:
            perf_data['successful_calls'] += 1
        else:
            perf_data['failed_calls'] += 1

        # Update execution time stats
        perf_data['avg_execution_time'] = (
            (perf_data['avg_execution_time'] * (perf_data['total_calls'] - 1)) + execution_time
        ) / perf_data['total_calls']

        perf_data['min_execution_time'] = min(perf_data['min_execution_time'], execution_time)
        perf_data['max_execution_time'] = max(perf_data['max_execution_time'], execution_time)

        # Keep last 100 performance records
        perf_data['performance_history'].append({
            'timestamp': timestamp,
            'execution_time': execution_time,
            'success': success,
            'metadata': metadata or {}
        })

        if len(perf_data['performance_history']) > 100:
            perf_data['performance_history'] = perf_data['performance_history'][-100:]

        # Log performance
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"PERFORMANCE: {operation} | {status} | Time: {execution_time:.3f}s")

        self.save_data()

    # ============================================================================
    # ERROR TRACKING
    # ============================================================================

    def track_error(self, feature_name: str, error_type: str, error_message: str,
                   user_id: int = None, metadata: Dict = None):
        """Track errors for monitoring and debugging"""

        timestamp = datetime.now().isoformat()
        error_key = f"{feature_name}:{error_type}"

        if error_key not in self.monitoring_data['errors']:
            self.monitoring_data['errors'][error_key] = {
                'count': 0,
                'first_occurred': timestamp,
                'last_occurred': timestamp,
                'affected_users': set(),
                'error_samples': []
            }

        error_data = self.monitoring_data['errors'][error_key]

        error_data['count'] += 1
        error_data['last_occurred'] = timestamp

        if user_id:
            error_data['affected_users'].add(user_id)

        # Keep last 10 error samples
        error_data['error_samples'].append({
            'timestamp': timestamp,
            'user_id': user_id,
            'message': error_message[:200],  # Truncate long messages
            'metadata': metadata or {}
        })

        if len(error_data['error_samples']) > 10:
            error_data['error_samples'] = error_data['error_samples'][-10:]

        # Convert set to list for JSON serialization
        error_data['affected_users'] = list(error_data['affected_users'])

        # Log error
        self.logger.error(f"FEATURE_ERROR: {feature_name} | {error_type} | User: {user_id} | {error_message}")

        self.save_data()

    # ============================================================================
    # PREMIUM METRICS
    # ============================================================================

    def track_premium_metrics(self):
        """Track premium subscription and usage metrics"""

        # This would integrate with your payment system
        # For now, we'll track basic metrics from usage data

        features = self.monitoring_data['features']

        premium_features = ['risk_heatmap', 'risk_optimizer', 'mtf_analysis']
        premium_usage = {feature: features.get(feature, {}).get('total_uses', 0)
                        for feature in premium_features}

        total_premium_usage = sum(premium_usage.values())

        self.monitoring_data['premium_metrics'] = {
            'last_updated': datetime.now().isoformat(),
            'total_premium_usage': total_premium_usage,
            'feature_breakdown': premium_usage,
            'conversion_rate_estimate': self._calculate_conversion_estimate()
        }

        self.save_data()

    def _calculate_conversion_estimate(self):
        """Estimate free to premium conversion rate"""
        features = self.monitoring_data['features']

        # Simple estimation based on premium feature usage
        premium_uses = 0
        free_uses = 0

        for feature_name, feature_data in features.items():
            tier_breakdown = feature_data.get('tier_breakdown', {})

            if feature_name in ['risk_heatmap', 'risk_optimizer', 'mtf_analysis']:
                premium_uses += tier_breakdown.get('premium', 0) + tier_breakdown.get('vip', 0)
            else:
                free_uses += tier_breakdown.get('free', 0)

        total_uses = premium_uses + free_uses
        if total_uses > 0:
            return premium_uses / total_uses
        return 0

    # ============================================================================
    # REPORTING
    # ============================================================================

    def generate_report(self, days: int = 7) -> Dict:
        """Generate a monitoring report for the last N days"""

        cutoff_date = datetime.now() - timedelta(days=days)

        report = {
            'period': f"{days} days",
            'generated_at': datetime.now().isoformat(),
            'feature_usage': {},
            'performance_metrics': {},
            'error_summary': {},
            'premium_insights': {}
        }

        # Feature usage report
        for feature_name, feature_data in self.monitoring_data['features'].items():
            daily_usage = feature_data.get('daily_usage', {})

            # Filter to last N days
            recent_usage = {date: count for date, count in daily_usage.items()
                          if datetime.fromisoformat(date) >= cutoff_date}

            report['feature_usage'][feature_name] = {
                'total_uses': sum(recent_usage.values()),
                'daily_average': sum(recent_usage.values()) / max(1, len(recent_usage)),
                'tier_breakdown': feature_data.get('tier_breakdown', {}),
                'success_rate': (feature_data.get('successful_uses', 0) /
                               max(1, feature_data.get('total_uses', 1)))
            }

        # Performance metrics
        for operation, perf_data in self.monitoring_data['performance'].items():
            report['performance_metrics'][operation] = {
                'avg_execution_time': perf_data.get('avg_execution_time', 0),
                'success_rate': (perf_data.get('successful_calls', 0) /
                               max(1, perf_data.get('total_calls', 1))),
                'total_calls': perf_data.get('total_calls', 0)
            }

        # Error summary
        for error_key, error_data in self.monitoring_data['errors'].items():
            last_occurred = error_data.get('last_occurred', '')
            if last_occurred and datetime.fromisoformat(last_occurred) >= cutoff_date:
                report['error_summary'][error_key] = {
                    'count': error_data.get('count', 0),
                    'affected_users': len(error_data.get('affected_users', [])),
                    'last_occurred': last_occurred
                }

        # Premium insights
        premium_metrics = self.monitoring_data.get('premium_metrics', {})
        report['premium_insights'] = {
            'total_premium_usage': premium_metrics.get('total_premium_usage', 0),
            'estimated_conversion_rate': premium_metrics.get('conversion_rate_estimate', 0),
            'feature_popularity': premium_metrics.get('feature_breakdown', {})
        }

        return report

    def get_health_status(self) -> Dict:
        """Get overall system health status"""

        # Check if critical features are working
        critical_features = ['risk_heatmap', 'risk_optimizer', 'mtf_analysis']
        working_features = 0

        for feature in critical_features:
            if feature in self.monitoring_data['features']:
                feature_data = self.monitoring_data['features'][feature]
                success_rate = (feature_data.get('successful_uses', 0) /
                              max(1, feature_data.get('total_uses', 1)))
                if success_rate > 0.8:  # 80% success rate
                    working_features += 1

        health_score = working_features / len(critical_features)

        status = {
            'overall_health': health_score,
            'status': 'HEALTHY' if health_score >= 0.8 else 'WARNING' if health_score >= 0.5 else 'CRITICAL',
            'critical_features_working': f"{working_features}/{len(critical_features)}",
            'last_updated': datetime.now().isoformat()
        }

        # Check for recent errors
        recent_errors = 0
        cutoff = datetime.now() - timedelta(hours=1)

        for error_data in self.monitoring_data['errors'].values():
            last_error = error_data.get('last_occurred', '')
            if last_error and datetime.fromisoformat(last_error) >= cutoff:
                recent_errors += 1

        status['recent_errors'] = recent_errors

        return status

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def track_feature_usage_decorator(feature_name: str):
    """Decorator to automatically track feature usage"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                # Extract user_id and user_tier from function arguments
                user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
                user_tier = kwargs.get('user_tier') or 'free'  # Default to free

                result = func(*args, **kwargs)

                execution_time = time.time() - start_time

                # Track successful usage
                monitor = FeatureMonitor()
                monitor.track_feature_usage(
                    feature_name=feature_name,
                    user_id=user_id,
                    user_tier=user_tier,
                    success=True,
                    execution_time=execution_time,
                    metadata={'function': func.__name__}
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time

                # Track failed usage
                monitor = FeatureMonitor()
                monitor.track_feature_usage(
                    feature_name=feature_name,
                    user_id=user_id,
                    user_tier=user_tier,
                    success=False,
                    execution_time=execution_time,
                    metadata={'error': str(e), 'function': func.__name__}
                )

                monitor.track_error(
                    feature_name=feature_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    user_id=user_id
                )

                raise e

        return wrapper
    return decorator

# ============================================================================
# GLOBAL MONITOR INSTANCE
# ============================================================================

monitor = FeatureMonitor()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage
    monitor = FeatureMonitor()

    # Track some example usage
    monitor.track_feature_usage(
        feature_name='risk_heatmap',
        user_id=12345,
        user_tier='premium',
        success=True,
        execution_time=1.2,
        metadata={'pairs': ['EURUSD', 'GBPUSD']}
    )

    monitor.track_feature_usage(
        feature_name='mtf_analysis',
        user_id=67890,
        user_tier='free',
        success=True,
        execution_time=0.8,
        metadata={'pair': 'BTC', 'timeframes': ['M15', 'H1', 'H4', 'D1']}
    )

    # Track performance
    monitor.track_performance(
        operation='risk_calculation',
        execution_time=0.15,
        success=True,
        metadata={'scenario': 'conservative'}
    )

    # Generate report
    report = monitor.generate_report(days=7)
    print("7-Day Monitoring Report:")
    print(json.dumps(report, indent=2, default=str))

    # Health check
    health = monitor.get_health_status()
    print(f"\nSystem Health: {health['status']} ({health['overall_health']:.1%})")



