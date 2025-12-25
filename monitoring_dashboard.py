#!/usr/bin/env python3
"""
Monitoring Dashboard for Premium Features
Basic health check for the new risk management and MTF analysis features
"""

import json
import os
from datetime import datetime

def check_feature_files():
    """Check if all feature files exist and are accessible"""

    required_files = [
        'risk_manager.py',
        'multi_timeframe_analyzer.py',
        'feature_monitoring.py',
        'telegram_bot.py',
        'test_new_features.py'
    ]

    print("CHECKING FEATURE FILES")
    print("-" * 40)

    all_present = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"{file:25} | {size:6d} bytes | PRESENT")
        else:
            print(f"{file:25} |         | MISSING")
            all_present = False

    return all_present

def test_imports():
    """Test if all modules can be imported"""

    print("\nTESTING MODULE IMPORTS")
    print("-" * 40)

    test_imports = [
        ('risk_manager', 'Risk management system'),
        ('multi_timeframe_analyzer', 'MTF analysis system'),
        ('feature_monitoring', 'Feature monitoring'),
        ('telegram_bot', 'Telegram bot (test mode)')
    ]

    all_imported = True
    for module, description in test_imports:
        try:
            if module == 'telegram_bot':
                os.environ['TEST_MODE'] = 'true'
                __import__(module)
                del os.environ['TEST_MODE']
            else:
                __import__(module)

            print(f"{description:25} | SUCCESS")
        except Exception as e:
            print(f"{description:25} | FAILED: {str(e)[:50]}")
            all_imported = False

    return all_imported

def check_monitoring_setup():
    """Check if monitoring files exist"""

    print("\nCHECKING MONITORING SETUP")
    print("-" * 40)

    monitoring_file = 'feature_monitoring.json'
    if os.path.exists(monitoring_file):
        size = os.path.getsize(monitoring_file)
        print(f"Monitoring data file    | {size:6d} bytes | READY")
        return True
    else:
        print(f"Monitoring data file    |         | NOT INITIALIZED")
        print("Note: Monitoring data will be created on first use")
        return False

def generate_health_report():
    """Generate a basic health report"""

    print("\nGENERATING HEALTH REPORT")
    print("="*60)

    report = {
        'generated_at': datetime.now().isoformat(),
        'overall_status': 'UNKNOWN',
        'checks': {},
        'recommendations': []
    }

    # Run checks
    files_ok = check_feature_files()
    imports_ok = test_imports()
    monitoring_ok = check_monitoring_setup()

    report['checks'] = {
        'feature_files': files_ok,
        'module_imports': imports_ok,
        'monitoring_setup': monitoring_ok
    }

    # Determine overall status
    if files_ok and imports_ok:
        report['overall_status'] = 'HEALTHY'
        report['recommendations'] = [
            'Deploy to production server with internet connectivity',
            'Configure proper Telegram bot token',
            'Set up automated monitoring alerts',
            'Begin user testing and feature validation'
        ]
    elif files_ok:
        report['overall_status'] = 'WARNING'
        report['recommendations'] = [
            'Fix import errors before deployment',
            'Check Python dependencies',
            'Review error messages above'
        ]
    else:
        report['overall_status'] = 'CRITICAL'
        report['recommendations'] = [
            'Restore missing feature files',
            'Re-run feature implementation',
            'Check file system integrity'
        ]

    print(f"\nOverall Status: {report['overall_status']}")
    print("\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")

    return report

    # Generate 7-day report
    report = monitor.generate_report(days=7)

    print(f"Report Period: {report['period']}")
    print(f"Generated: {report['generated_at']}")
    print()

    # Feature Usage Summary
    print("FEATURE USAGE SUMMARY")
    print("-" * 40)

    total_usage = 0
    premium_usage = 0

    for feature_name, feature_data in report['feature_usage'].items():
        total_uses = feature_data['total_uses']
        total_usage += total_uses

        # Calculate premium usage (non-free tier)
        tier_breakdown = feature_data['tier_breakdown']
        premium_uses = tier_breakdown.get('premium', 0) + tier_breakdown.get('vip', 0)
        premium_usage += premium_uses

        success_rate = feature_data['success_rate'] * 100

        print(f"{feature_name:15} | {total_uses:4d} uses | {success_rate:5.1f}% success | Premium: {premium_uses}")

    print("-" * 40)
    print(f"Total Usage: {total_usage} | Premium Usage: {premium_usage}")
    if total_usage > 0:
        conversion_rate = premium_usage / total_usage * 100
        print(".1f")
    print()

    # Performance Metrics
    print("PERFORMANCE METRICS")
    print("-" * 40)

    for operation, perf_data in report['performance_metrics'].items():
        avg_time = perf_data['avg_execution_time'] * 1000  # Convert to ms
        success_rate = perf_data['success_rate'] * 100
        total_calls = perf_data['total_calls']

        print(".1f")
    print()

    # Error Summary
    print("ERROR SUMMARY (Last 7 days)")
    print("-" * 40)

    if report['error_summary']:
        for error_key, error_data in report['error_summary'].items():
            print(f"{error_key}: {error_data['count']} occurrences, {error_data['affected_users']} users")
    else:
        print("No significant errors in the last 7 days ✓")
    print()

    # Premium Insights
    print("PREMIUM INSIGHTS")
    print("-" * 40)

    insights = report['premium_insights']
    total_premium = insights['total_premium_usage']
    conversion = insights['estimated_conversion_rate'] * 100
    popularity = insights['feature_popularity']

    print(f"Total Premium Usage: {total_premium}")
    print(".1f")
    print()
    print("Feature Popularity:")
    for feature, uses in popularity.items():
        print(f"  {feature}: {uses} uses")

    return report

def check_system_health():
    """Check overall system health"""

    print("\n🏥 SYSTEM HEALTH CHECK")
    print("="*60)

    health = monitor.get_health_status()

    status = health['status']
    score = health['overall_health']
    working = health['critical_features_working']
    recent_errors = health['recent_errors']

    print(f"Overall Status: {status}")
    print(".1f")
    print(f"Critical Features: {working}")
    print(f"Recent Errors: {recent_errors}")
    print()

    # Health indicators
    if score >= 0.8:
        print("✅ SYSTEM HEALTHY - All critical features working")
    elif score >= 0.5:
        print("⚠️  SYSTEM WARNING - Some features may be degraded")
    else:
        print("❌ SYSTEM CRITICAL - Immediate attention required")

    if recent_errors > 5:
        print(f"⚠️  HIGH ERROR RATE - {recent_errors} errors in last hour")
    elif recent_errors > 0:
        print(f"ℹ️  MINOR ISSUES - {recent_errors} errors in last hour")
    else:
        print("✅ NO RECENT ERRORS")

    return health

def generate_recommendations(report, health):
    """Generate actionable recommendations based on monitoring data"""

    print("\n💡 RECOMMENDATIONS")
    print("="*60)

    recommendations = []

    # Check feature usage
    low_usage_features = []
    for feature_name, feature_data in report['feature_usage'].items():
        if feature_data['total_uses'] < 10:  # Less than 10 uses in 7 days
            low_usage_features.append(feature_name)

    if low_usage_features:
        recommendations.append(f"📈 INCREASE MARKETING for low-usage features: {', '.join(low_usage_features)}")
        recommendations.append("   Consider targeted campaigns or tutorial improvements")

    # Check error rates
    high_error_features = []
    for feature_name, feature_data in report['feature_usage'].items():
        if feature_data['success_rate'] < 0.8:  # Less than 80% success
            high_error_features.append(feature_name)

    if high_error_features:
        recommendations.append(f"🐛 FIX ERRORS in features with low success rates: {', '.join(high_error_features)}")
        recommendations.append("   Review error logs and improve error handling")

    # Check performance
    slow_features = []
    for operation, perf_data in report['performance_metrics'].items():
        if perf_data['avg_execution_time'] > 2.0:  # Slower than 2 seconds
            slow_features.append(operation)

    if slow_features:
        recommendations.append(f"⚡ OPTIMIZE PERFORMANCE for slow operations: {', '.join(slow_features)}")
        recommendations.append("   Consider caching, async processing, or code optimization")

    # Check premium conversion
    conversion = report['premium_insights']['estimated_conversion_rate']
    if conversion < 0.1:  # Less than 10% conversion
        recommendations.append("💰 IMPROVE PREMIUM CONVERSION")
        recommendations.append("   Enhance premium feature demos and value propositions")
    elif conversion > 0.3:  # Good conversion
        recommendations.append("✅ PREMIUM CONVERSION HEALTHY - Continue current strategy")

    # System health
    if health['status'] != 'HEALTHY':
        recommendations.append("🔧 ADDRESS SYSTEM HEALTH ISSUES")
        recommendations.append("   Check critical features and resolve any outages")

    # Default recommendations if everything is good
    if not recommendations:
        recommendations.append("✅ SYSTEM PERFORMING WELL")
        recommendations.append("   Continue monitoring and consider feature expansions")

    for rec in recommendations:
        print(rec)

def save_report_to_file(report, health):
    """Save the monitoring report to a file"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"monitoring_report_{timestamp}.json"

    full_report = {
        'generated_at': datetime.now().isoformat(),
        'report': report,
        'health': health,
        'recommendations': generate_recommendations(report, health)
    }

    with open(filename, 'w') as f:
        json.dump(full_report, f, indent=2, default=str)

    print(f"\n📄 Report saved to: {filename}")

def main():
    """Main monitoring dashboard function"""

    print("PREMIUM FEATURES MONITORING DASHBOARD")
    print("="*60)
    print(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    try:
        # Generate monitoring report
        report = generate_monitoring_report()

        # Check system health
        health = check_system_health()

        # Generate recommendations
        generate_recommendations(report, health)

        # Save report
        save_report_to_file(report, health)

        print("\n" + "="*60)
        print("✅ MONITORING DASHBOARD COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"❌ ERROR GENERATING MONITORING REPORT: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main monitoring dashboard function"""

    print("PREMIUM FEATURES MONITORING DASHBOARD")
    print("="*60)
    print("Dashboard generated: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("="*60)

    try:
        report = generate_health_report()

        print("\n" + "="*60)
        if report['overall_status'] == 'HEALTHY':
            print("STATUS: ALL SYSTEMS GO - READY FOR PRODUCTION")
        else:
            print("STATUS: {} - REVIEW ISSUES ABOVE".format(report['overall_status']))
        print("="*60)

        # Save report
        filename = "health_report_{}.json".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print("Report saved to: {}".format(filename))

    except Exception as e:
        print("ERROR GENERATING MONITORING REPORT: {}".format(str(e)))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()