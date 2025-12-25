"""
Error Learning Dashboard for Professional Trading Bot
Comprehensive monitoring and analytics for machine learning-based error prevention
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from global_error_learning import global_error_manager, get_error_insights, get_adaptive_recommendations

logger = logging.getLogger(__name__)

class ErrorDashboard:
    """Professional error monitoring and analytics dashboard"""

    def __init__(self):
        self.dashboard_data = {}
        self.alerts = []
        self.performance_history = []
        self.update_interval = 60  # Update every minute

    def get_system_overview(self) -> Dict:
        """Get comprehensive system error overview"""
        insights = get_error_insights()

        return {
            'timestamp': datetime.now().isoformat(),
            'system_health_score': insights.get('system_health_score', 0),
            'total_operations': insights.get('total_operations', 0),
            'learning_progress': insights.get('learning_progress', 0),
            'recent_error_rate': insights.get('recent_error_rate', 0),
            'model_trained': insights.get('model_trained', False),
            'training_data_size': insights.get('training_data_size', 0),
            'performance_metrics': insights.get('performance_metrics', {}),
            'most_problematic_components': insights.get('most_problematic_components', [])[:5]
        }

    def get_component_details(self, component: str) -> Dict:
        """Get detailed error analytics for a specific component"""
        insights = get_error_insights(component)

        if not insights.get('error_patterns'):
            return {'component': component, 'status': 'no_data'}

        pattern = insights['error_patterns'].get(component, {})

        return {
            'component': component,
            'total_operations': pattern.get('total_operations', 0),
            'error_rate': pattern.get('error_rate', 0),
            'avg_execution_time': pattern.get('avg_execution_time', 0),
            'common_error_times': pattern.get('common_error_times', []),
            'error_recovery_time': pattern.get('error_recovery_time', []),
            'performance_trends': pattern.get('performance_trends', []),
            'last_updated': datetime.now().isoformat()
        }

    def get_error_predictions(self, component: str, operation_context: Dict) -> Dict:
        """Get error predictions for a specific operation"""
        prediction = global_error_manager.predict_error_likelihood(component, operation_context)
        recommendations = get_adaptive_recommendations(component, operation_context)

        return {
            'component': component,
            'operation_context': operation_context,
            'error_probability': prediction.get('error_probability', 0),
            'confidence': prediction.get('confidence', 0),
            'should_attempt': prediction.get('should_attempt', True),
            'risk_level': prediction.get('risk_level', 'low'),
            'alternative_suggestions': prediction.get('alternative_suggestions', []),
            'adaptive_recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }

    def get_alerts_and_warnings(self) -> List[Dict]:
        """Generate alerts based on error patterns and system health"""
        alerts = []
        insights = get_error_insights()

        # System health alerts
        health_score = insights.get('system_health_score', 100)
        if health_score < 50:
            alerts.append({
                'level': 'CRITICAL',
                'type': 'system_health',
                'message': f'System health critically low: {health_score:.1f}/100',
                'recommendation': 'Immediate system review and maintenance required',
                'timestamp': datetime.now().isoformat()
            })
        elif health_score < 70:
            alerts.append({
                'level': 'WARNING',
                'type': 'system_health',
                'message': f'System health degraded: {health_score:.1f}/100',
                'recommendation': 'Monitor closely and consider maintenance',
                'timestamp': datetime.now().isoformat()
            })

        # Component-specific alerts
        for comp_data in insights.get('most_problematic_components', []):
            error_rate = comp_data.get('error_rate', 0)
            component = comp_data.get('component', 'unknown')

            if error_rate > 0.5:  # >50% error rate
                alerts.append({
                    'level': 'CRITICAL',
                    'type': 'component_error_rate',
                    'component': component,
                    'message': f'{component} error rate critically high: {error_rate:.1%}',
                    'recommendation': 'Review and optimize component, consider fallback strategies',
                    'timestamp': datetime.now().isoformat()
                })
            elif error_rate > 0.2:  # >20% error rate
                alerts.append({
                    'level': 'WARNING',
                    'type': 'component_error_rate',
                    'component': component,
                    'message': f'{component} error rate elevated: {error_rate:.1%}',
                    'recommendation': 'Monitor component performance and consider improvements',
                    'timestamp': datetime.now().isoformat()
                })

        # Learning progress alerts
        learning_progress = insights.get('learning_progress', 0)
        if learning_progress < 0.3:
            alerts.append({
                'level': 'INFO',
                'type': 'learning_progress',
                'message': f'Error learning progress low: {learning_progress:.1%}',
                'recommendation': 'Continue operations to build learning dataset',
                'timestamp': datetime.now().isoformat()
            })

        return alerts

    def get_performance_analytics(self, hours: int = 24) -> Dict:
        """Get performance analytics over specified time period"""
        # This would typically query historical data
        # For now, return current insights with time context

        insights = get_error_insights()

        return {
            'time_period_hours': hours,
            'total_operations': insights.get('total_operations', 0),
            'error_rate_trend': self._calculate_error_trend(hours),
            'component_performance': self._get_component_performance(hours),
            'learning_efficiency': self._calculate_learning_efficiency(),
            'error_prevention_effectiveness': self._calculate_prevention_effectiveness(),
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_error_trend(self, hours: int) -> Dict:
        """Calculate error rate trend over time"""
        # Simplified trend calculation
        insights = get_error_insights()
        recent_rate = insights.get('recent_error_rate', 0)

        # Mock historical comparison (in real implementation, this would use stored data)
        historical_rate = recent_rate * 1.2  # Assume historical was 20% higher

        trend = 'improving' if recent_rate < historical_rate else 'worsening'
        change_pct = ((recent_rate - historical_rate) / historical_rate) * 100 if historical_rate > 0 else 0

        return {
            'current_rate': recent_rate,
            'historical_rate': historical_rate,
            'trend': trend,
            'change_percent': change_pct,
            'period_hours': hours
        }

    def _get_component_performance(self, hours: int) -> List[Dict]:
        """Get performance data for each component"""
        insights = get_error_insights()
        components = []

        for comp in ['telegram_bot', 'execution_manager', 'risk_manager', 'data_fetcher', 'backtest_engine', 'signal_generator']:
            comp_insights = get_error_insights(comp)
            pattern = comp_insights.get('error_patterns', {}).get(comp, {})

            components.append({
                'component': comp,
                'error_rate': pattern.get('error_rate', 0),
                'total_operations': pattern.get('total_operations', 0),
                'avg_execution_time': pattern.get('avg_execution_time', 0),
                'status': 'healthy' if pattern.get('error_rate', 0) < 0.1 else 'warning' if pattern.get('error_rate', 0) < 0.3 else 'critical'
            })

        return components

    def _calculate_learning_efficiency(self) -> float:
        """Calculate how efficiently the system is learning from errors"""
        insights = get_error_insights()
        metrics = insights.get('performance_metrics', {})

        total_operations = metrics.get('total_operations', 0)
        learning_progress = insights.get('learning_progress', 0)

        if total_operations == 0:
            return 0.0

        # Efficiency = learning progress / operations (normalized)
        efficiency = min(1.0, (learning_progress * 100) / max(1, total_operations / 10))
        return efficiency

    def _calculate_prevention_effectiveness(self) -> float:
        """Calculate how effective error prevention is"""
        insights = get_error_insights()
        metrics = insights.get('performance_metrics', {})

        errors_avoided = metrics.get('errors_avoided', 0)
        successful_predictions = metrics.get('successful_predictions', 0)
        total_preventions = errors_avoided + successful_predictions

        if total_preventions == 0:
            return 0.0

        # Effectiveness = successful preventions / total prevention attempts
        effectiveness = successful_predictions / total_preventions if total_preventions > 0 else 0.0
        return effectiveness

    def generate_report(self, report_type: str = 'full') -> str:
        """Generate a comprehensive error report"""
        overview = self.get_system_overview()
        alerts = self.get_alerts_and_warnings()
        analytics = self.get_performance_analytics()

        report = f"""
🚨 ERROR LEARNING DASHBOARD REPORT 🚨
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SYSTEM OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• System Health Score: {overview['system_health_score']:.1f}/100
• Total Operations: {overview['total_operations']:,}
• Learning Progress: {overview['learning_progress']:.1%}
• Recent Error Rate: {overview['recent_error_rate']:.2%}
• Model Trained: {'✅' if overview['model_trained'] else '❌'}
• Training Data Size: {overview['training_data_size']:,}

⚠️ ACTIVE ALERTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if alerts:
            for alert in alerts[:10]:  # Show top 10 alerts
                level_emoji = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': 'ℹ️'}.get(alert['level'], '❓')
                report += f"{level_emoji} {alert['level']}: {alert['message']}\n"
                report += f"   💡 {alert['recommendation']}\n\n"
        else:
            report += "✅ No active alerts - system operating normally\n\n"

        report += f"""
📈 PERFORMANCE ANALYTICS (24h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Error Rate Trend: {analytics['error_rate_trend']['trend'].title()}
• Change: {analytics['error_rate_trend']['change_percent']:+.1f}%
• Learning Efficiency: {analytics['learning_efficiency']:.1%}
• Prevention Effectiveness: {analytics['error_prevention_effectiveness']:.1%}

🔧 COMPONENT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for comp in analytics['component_performance']:
            status_emoji = {'healthy': '🟢', 'warning': '🟡', 'critical': '🔴'}.get(comp['status'], '❓')
            report += f"{status_emoji} {comp['component']}: {comp['error_rate']:.1%} errors ({comp['total_operations']} ops)\n"

        if report_type == 'full':
            report += f"""

🎯 MOST PROBLEMATIC COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for comp in overview.get('most_problematic_components', [])[:5]:
                report += f"• {comp['component']}: {comp['error_rate']:.1%} error rate\n"

        report += f"""

💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Continue building operation history for better learning
• Monitor high-error components closely
• Review and optimize error-prone operations
• Consider implementing additional fallback strategies

📞 For technical support or system optimization, contact the development team.
"""

        return report

    def export_data(self, format_type: str = 'json') -> str:
        """Export dashboard data in various formats"""
        data = {
            'overview': self.get_system_overview(),
            'alerts': self.get_alerts_and_warnings(),
            'analytics': self.get_performance_analytics(),
            'export_timestamp': datetime.now().isoformat()
        }

        if format_type == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format_type == 'csv':
            # Simplified CSV export of component performance
            analytics = data['analytics']
            csv_lines = ["Component,Error Rate,Total Operations,Status"]
            for comp in analytics.get('component_performance', []):
                csv_lines.append(f"{comp['component']},{comp['error_rate']},{comp['total_operations']},{comp['status']}")
            return "\n".join(csv_lines)
        else:
            return str(data)

# Global dashboard instance
error_dashboard = ErrorDashboard()

def get_dashboard_report(report_type: str = 'full') -> str:
    """Convenience function to get dashboard report"""
    return error_dashboard.generate_report(report_type)

def get_system_health() -> Dict:
    """Convenience function to get system health overview"""
    return error_dashboard.get_system_overview()

def check_alerts() -> List[Dict]:
    """Convenience function to check active alerts"""
    return error_dashboard.get_alerts_and_warnings()

if __name__ == "__main__":
    # Test the dashboard
    print("🧠 Error Learning Dashboard Test")
    print("=" * 50)

    # Generate and display report
    report = get_dashboard_report('full')
    print(report)

    # Show system health
    health = get_system_health()
    print("\n📊 System Health Summary:")
    print(f"  Health Score: {health['system_health_score']:.1f}/100")
    print(f"  Operations: {health['total_operations']:,}")
    print(f"  Error Rate: {health['recent_error_rate']:.2%}")
    print(f"  Learning Progress: {health['learning_progress']:.1%}")

    # Check alerts
    alerts = check_alerts()
    if alerts:
        print(f"\n⚠️ Active Alerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3
            print(f"  {alert['level']}: {alert['message']}")
    else:
        print("\n✅ No active alerts")

    print("\n✅ Error Dashboard test completed!")
