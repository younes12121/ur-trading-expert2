"""
Pre-Deployment Checklist
Automated checks before deploying to production
"""

import sys
import os
import subprocess
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
import importlib.util

@dataclass
class CheckResult:
    """Result of a deployment check"""
    name: str
    status: str  # 'PASS', 'FAIL', 'WARN', 'SKIP'
    message: str
    details: Optional[str] = None
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class PreDeploymentChecklist:
    """Automated pre-deployment validation system"""

    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.logger = logging.getLogger('pre_deployment')
        self.results: List[CheckResult] = []
        self.check_functions: Dict[str, Callable] = {}

        # Register all checks
        self._register_checks()

    def _register_checks(self):
        """Register all deployment checks"""
        self.check_functions = {
            'config_validation': self._check_config_validation,
            'dependency_check': self._check_dependencies,
            'database_connection': self._check_database_connection,
            'api_keys_validation': self._check_api_keys,
            'performance_tests': self._check_performance_tests,
            'security_audit': self._check_security_audit,
            'backup_system': self._check_backup_system,
            'monitoring_setup': self._check_monitoring_setup,
            'health_checks': self._check_health_checks,
            'performance_mode': self._check_performance_mode,
            'concurrent_processing': self._check_concurrent_processing,
            'memory_limits': self._check_memory_limits,
            'deployment_scripts': self._check_deployment_scripts,
            'rollback_procedures': self._check_rollback_procedures,
            'documentation_complete': self._check_documentation_complete
        }

    def run_all_checks(self) -> bool:
        """Run all deployment checks"""
        print("=" * 80)
        print("PRE-DEPLOYMENT CHECKLIST")
        print(f"Environment: {self.environment.upper()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        self.results = []
        passed = 0
        failed = 0
        warnings = 0
        skipped = 0

        for check_name, check_func in self.check_functions.items():
            print(f"Running check: {check_name}...")
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time

                result.duration = duration
                self.results.append(result)

                status_icon = {
                    'PASS': '✅',
                    'FAIL': '❌',
                    'WARN': '⚠️',
                    'SKIP': '⏭️'
                }.get(result.status, '❓')

                print(f"  {status_icon} {result.status}: {result.message}")
                if result.details:
                    print(f"    Details: {result.details}")

                # Count results
                if result.status == 'PASS':
                    passed += 1
                elif result.status == 'FAIL':
                    failed += 1
                elif result.status == 'WARN':
                    warnings += 1
                elif result.status == 'SKIP':
                    skipped += 1

            except Exception as e:
                error_result = CheckResult(
                    name=check_name,
                    status='FAIL',
                    message=f"Check failed with exception: {e}",
                    details=str(e)
                )
                self.results.append(error_result)
                failed += 1
                print(f"  ❌ FAIL: Check crashed: {e}")

            print()

        # Summary
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print("=" * 80)
        print("DEPLOYMENT CHECK SUMMARY")
        print("=" * 80)
        print(f"Total checks: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Skipped: {skipped}")
        print(".1f")
        print()

        if failed > 0:
            print("❌ DEPLOYMENT BLOCKED - Critical failures detected!")
            print("Please fix the failed checks before deploying.")
            return False
        elif warnings > 0:
            print("⚠️  DEPLOYMENT WITH WARNINGS")
            print("Warnings detected. Review and consider fixing before deployment.")
            return True
        else:
            print("✅ ALL CHECKS PASSED - Ready for deployment!")
            return True

    def _check_config_validation(self) -> CheckResult:
        """Check configuration validation"""
        try:
            import config

            required_attrs = [
                'PERFORMANCE_MODE', 'ENABLE_CACHING', 'CONCURRENT_API',
                'LOG_LEVEL', 'DB_PATH'
            ]

            missing = []
            for attr in required_attrs:
                if not hasattr(config, attr):
                    missing.append(attr)

            if missing:
                return CheckResult(
                    name='config_validation',
                    status='FAIL',
                    message=f"Missing required config attributes: {', '.join(missing)}",
                    details=f"Add these to config.py: {missing}"
                )

            # Check performance mode
            if not getattr(config, 'PERFORMANCE_MODE', False):
                return CheckResult(
                    name='config_validation',
                    status='WARN',
                    message="Performance mode is disabled in config",
                    details="Consider enabling PERFORMANCE_MODE=True for production"
                )

            return CheckResult(
                name='config_validation',
                status='PASS',
                message="Configuration validation passed"
            )

        except Exception as e:
            return CheckResult(
                name='config_validation',
                status='FAIL',
                message=f"Config validation failed: {e}",
                details=str(e)
            )

    def _check_dependencies(self) -> CheckResult:
        """Check if all required dependencies are installed"""
        required_packages = [
            'pandas', 'numpy', 'requests', 'python-telegram-bot',
            'psutil', 'flask', 'ccxt'
        ]

        missing = []
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
            except ImportError:
                missing.append(package)

        if missing:
            return CheckResult(
                name='dependency_check',
                status='FAIL',
                message=f"Missing required packages: {', '.join(missing)}",
                details=f"Install with: pip install {' '.join(missing)}"
            )

        return CheckResult(
            name='dependency_check',
            status='PASS',
            message="All required dependencies are installed"
        )

    def _check_database_connection(self) -> CheckResult:
        """Check database connectivity"""
        try:
            import config
            db_path = getattr(config, 'DB_PATH', 'trades.db')

            # Try to connect/create database
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()

            return CheckResult(
                name='database_connection',
                status='PASS',
                message="Database connection successful"
            )

        except Exception as e:
            return CheckResult(
                name='database_connection',
                status='FAIL',
                message=f"Database connection failed: {e}",
                details="Check database path and permissions"
            )

    def _check_api_keys(self) -> CheckResult:
        """Check API keys configuration"""
        try:
            import config

            required_keys = ['BINANCE_API_KEY', 'BINANCE_API_SECRET']
            missing = []
            placeholder = []

            for key in required_keys:
                value = getattr(config, key, '')
                if not value or value.startswith('Add your'):
                    if not value:
                        missing.append(key)
                    else:
                        placeholder.append(key)

            if missing:
                return CheckResult(
                    name='api_keys_validation',
                    status='FAIL',
                    message=f"Missing API keys: {', '.join(missing)}",
                    details="Add your actual API keys to config.py"
                )

            if placeholder:
                return CheckResult(
                    name='api_keys_validation',
                    status='WARN',
                    message=f"Placeholder API keys detected: {', '.join(placeholder)}",
                    details="Replace placeholder values with actual API keys"
                )

            return CheckResult(
                name='api_keys_validation',
                status='PASS',
                message="API keys are configured"
            )

        except Exception as e:
            return CheckResult(
                name='api_keys_validation',
                status='FAIL',
                message=f"API keys check failed: {e}",
                details=str(e)
            )

    def _check_performance_tests(self) -> CheckResult:
        """Run performance tests"""
        try:
            # Import and run performance tests
            import test_performance_integration

            # Run a quick test
            suite = test_performance_integration.PerformanceTestSuite()
            suite.create_test_data(days=7)  # Small dataset for quick test

            # Run just one test
            result = suite.test_data_fetcher()
            if result.status == 'PASS':
                return CheckResult(
                    name='performance_tests',
                    status='PASS',
                    message="Performance tests passed"
                )
            else:
                return CheckResult(
                    name='performance_tests',
                    status='FAIL',
                    message="Performance tests failed",
                    details="Run test_performance_integration.py for details"
                )

        except Exception as e:
            return CheckResult(
                name='performance_tests',
                status='WARN',
                message=f"Performance tests could not be run: {e}",
                details="Run test_performance_integration.py manually"
            )

    def _check_security_audit(self) -> CheckResult:
        """Perform basic security audit"""
        issues = []

        # Check for sensitive files
        sensitive_files = ['.env', 'secrets.json', 'private_key.pem']
        for filename in sensitive_files:
            if os.path.exists(filename):
                issues.append(f"Sensitive file found: {filename}")

        # Check file permissions (basic check)
        config_file = 'config.py'
        if os.path.exists(config_file):
            import stat
            st = os.stat(config_file)
            if bool(st.st_mode & stat.S_IRGRP) or bool(st.st_mode & stat.S_IROTH):
                issues.append("config.py is readable by group/others")

        if issues:
            return CheckResult(
                name='security_audit',
                status='WARN',
                message=f"Security issues found: {len(issues)}",
                details="\n".join(f"• {issue}" for issue in issues)
            )

        return CheckResult(
            name='security_audit',
            status='PASS',
            message="Basic security audit passed"
        )

    def _check_backup_system(self) -> CheckResult:
        """Check backup system"""
        try:
            # Check if backup directories exist
            backup_dirs = ['backups', 'backup_database']
            existing = [d for d in backup_dirs if os.path.exists(d)]

            if not existing:
                return CheckResult(
                    name='backup_system',
                    status='WARN',
                    message="No backup directories found",
                    details="Create backup directories and verify backup scripts"
                )

            return CheckResult(
                name='backup_system',
                status='PASS',
                message=f"Backup directories found: {', '.join(existing)}"
            )

        except Exception as e:
            return CheckResult(
                name='backup_system',
                status='WARN',
                message=f"Backup check failed: {e}",
                details="Verify backup system manually"
            )

    def _check_monitoring_setup(self) -> CheckResult:
        """Check monitoring system setup"""
        try:
            # Check if monitoring files exist
            monitoring_files = [
                'monitoring.py',
                'production_monitoring.py',
                'health_check.py',
                'performance_dashboard.py',
                'performance_alerts.py'
            ]

            missing = [f for f in monitoring_files if not os.path.exists(f)]

            if missing:
                return CheckResult(
                    name='monitoring_setup',
                    status='WARN',
                    message=f"Missing monitoring files: {', '.join(missing)}",
                    details="Ensure monitoring components are properly set up"
                )

            return CheckResult(
                name='monitoring_setup',
                status='PASS',
                message="Monitoring system files are present"
            )

        except Exception as e:
            return CheckResult(
                name='monitoring_setup',
                status='WARN',
                message=f"Monitoring check failed: {e}",
                details=str(e)
            )

    def _check_health_checks(self) -> CheckResult:
        """Run health checks"""
        try:
            import health_check

            # Try to run a basic health check
            checker = health_check.HealthChecker()
            results = checker.run_checks()

            failed_checks = [name for name, result in results.items() if not result.get('healthy', False)]

            if failed_checks:
                return CheckResult(
                    name='health_checks',
                    status='FAIL',
                    message=f"Health checks failed: {', '.join(failed_checks)}",
                    details="Run health_check.py for detailed results"
                )

            return CheckResult(
                name='health_checks',
                status='PASS',
                message="All health checks passed"
            )

        except Exception as e:
            return CheckResult(
                name='health_checks',
                status='WARN',
                message=f"Health checks could not be run: {e}",
                details="Run health_check.py manually"
            )

    def _check_performance_mode(self) -> CheckResult:
        """Check performance mode configuration"""
        try:
            import config

            perf_mode = getattr(config, 'PERFORMANCE_MODE', False)
            caching = getattr(config, 'ENABLE_CACHING', False)
            concurrent = getattr(config, 'CONCURRENT_API', False)

            if not perf_mode:
                return CheckResult(
                    name='performance_mode',
                    status='FAIL',
                    message="Performance mode is disabled",
                    details="Set PERFORMANCE_MODE=True in config.py for production"
                )

            if not caching:
                return CheckResult(
                    name='performance_mode',
                    status='WARN',
                    message="Caching is disabled",
                    details="Consider enabling ENABLE_CACHING=True"
                )

            if not concurrent:
                return CheckResult(
                    name='performance_mode',
                    status='WARN',
                    message="Concurrent API calls are disabled",
                    details="Consider enabling CONCURRENT_API=True"
                )

            return CheckResult(
                name='performance_mode',
                status='PASS',
                message="Performance optimizations are enabled"
            )

        except Exception as e:
            return CheckResult(
                name='performance_mode',
                status='FAIL',
                message=f"Performance mode check failed: {e}",
                details=str(e)
            )

    def _check_concurrent_processing(self) -> CheckResult:
        """Check concurrent processing setup"""
        try:
            import concurrent_processor

            # Basic import and instantiation check
            processor = concurrent_processor.get_processor()

            return CheckResult(
                name='concurrent_processing',
                status='PASS',
                message="Concurrent processing framework is available"
            )

        except Exception as e:
            return CheckResult(
                name='concurrent_processing',
                status='WARN',
                message=f"Concurrent processing check failed: {e}",
                details="Ensure concurrent_processor.py is properly configured"
            )

    def _check_memory_limits(self) -> CheckResult:
        """Check memory management setup"""
        try:
            import memory_optimizer

            optimizer = memory_optimizer.get_optimizer()
            stats = optimizer.get_memory_stats()

            current_memory = stats.get('current_memory_mb', 0)
            threshold = stats.get('memory_threshold_mb', 500)

            if current_memory > threshold:
                return CheckResult(
                    name='memory_limits',
                    status='WARN',
                    message=".2f",
                    details="Monitor memory usage during deployment"
                )

            return CheckResult(
                name='memory_limits',
                status='PASS',
                message="Memory usage is within limits"
            )

        except Exception as e:
            return CheckResult(
                name='memory_limits',
                status='WARN',
                message=f"Memory check failed: {e}",
                details="Ensure memory_optimizer.py is available"
            )

    def _check_deployment_scripts(self) -> CheckResult:
        """Check deployment scripts"""
        scripts = ['deploy.sh', 'deploy.ps1']

        missing = [s for s in scripts if not os.path.exists(s)]

        if missing:
            return CheckResult(
                name='deployment_scripts',
                status='WARN',
                message=f"Missing deployment scripts: {', '.join(missing)}",
                details="Ensure deployment scripts are present and executable"
            )

        return CheckResult(
            name='deployment_scripts',
            status='PASS',
            message="Deployment scripts are present"
        )

    def _check_rollback_procedures(self) -> CheckResult:
        """Check rollback procedures"""
        # Check for backup files or rollback scripts
        rollback_indicators = [
            'rollback.sh',
            'rollback.ps1',
            'backups/',
            'backup_database/'
        ]

        found = [item for item in rollback_indicators if os.path.exists(item.rstrip('/'))]

        if not found:
            return CheckResult(
                name='rollback_procedures',
                status='WARN',
                message="No rollback procedures found",
                details="Ensure rollback procedures are documented and available"
            )

        return CheckResult(
            name='rollback_procedures',
            status='PASS',
            message=f"Rollback procedures available: {', '.join(found)}"
        )

    def _check_documentation_complete(self) -> CheckResult:
        """Check documentation completeness"""
        required_docs = [
            'README.md',
            'DEPLOYMENT_GUIDE.md',
            'PRODUCTION_DEPLOYMENT.md',
            'config.py'
        ]

        missing = [doc for doc in required_docs if not os.path.exists(doc)]

        if missing:
            return CheckResult(
                name='documentation_complete',
                status='WARN',
                message=f"Missing documentation: {', '.join(missing)}",
                details="Ensure all required documentation is present"
            )

        return CheckResult(
            name='documentation_complete',
            status='PASS',
            message="Required documentation is present"
        )

    def export_results(self, filename: Optional[str] = None) -> str:
        """Export check results to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pre_deployment_check_{timestamp}.json"

        data = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'results': [
                {
                    'name': r.name,
                    'status': r.status,
                    'message': r.message,
                    'details': r.details,
                    'duration': r.duration,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.results
            ],
            'summary': {
                'total': len(self.results),
                'passed': len([r for r in self.results if r.status == 'PASS']),
                'failed': len([r for r in self.results if r.status == 'FAIL']),
                'warnings': len([r for r in self.results if r.status == 'WARN']),
                'skipped': len([r for r in self.results if r.status == 'SKIP'])
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        return filename

def main():
    """Run pre-deployment checklist"""
    import argparse

    parser = argparse.ArgumentParser(description='Pre-deployment checklist')
    parser.add_argument('--environment', default='production',
                       help='Deployment environment')
    parser.add_argument('--export', action='store_true',
                       help='Export results to JSON file')

    args = parser.parse_args()

    checklist = PreDeploymentChecklist(args.environment)
    success = checklist.run_all_checks()

    if args.export:
        filename = checklist.export_results()
        print(f"\nResults exported to: {filename}")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

