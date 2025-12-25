"""
Security Audit Module
Automated security checks and compliance verification
"""

import os
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Performs security audits and compliance checks"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        
    def check_environment_variables(self) -> List[Dict]:
        """Check for exposed secrets in environment"""
        issues = []
        
        # Check for hardcoded secrets
        sensitive_patterns = [
            r'password\s*=\s*["\']([^"\']+)["\']',
            r'api_key\s*=\s*["\']([^"\']+)["\']',
            r'secret\s*=\s*["\']([^"\']+)["\']',
            r'token\s*=\s*["\']([^"\']+)["\']',
        ]
        
        # Check common files
        files_to_check = [
            'telegram_bot.py',
            'payment_handler.py',
            'broker_connector.py',
            'config.py',
            'bot_config.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in sensitive_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if match.group(1) not in ['', 'your_key_here', 'change_me']:
                                    issues.append({
                                        'file': file_path,
                                        'type': 'hardcoded_secret',
                                        'severity': 'high',
                                        'line': content[:match.start()].count('\n') + 1,
                                        'pattern': match.group(0)[:50]
                                    })
                except Exception as e:
                    logger.warning(f"Could not check {file_path}: {e}")
        
        return issues
    
    def check_ssl_configuration(self) -> Dict:
        """Check SSL/TLS configuration"""
        checks = {
            'ssl_enabled': False,
            'certificate_valid': False,
            'tls_version': None,
            'issues': []
        }
        
        # Check for SSL configuration in deployment files
        ssl_files = ['docker-compose.yml', 'nginx.conf', 'app.yaml']
        for file_path in ssl_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if '443' in content or 'ssl' in content.lower() or 'tls' in content.lower():
                        checks['ssl_enabled'] = True
                        break
        
        if not checks['ssl_enabled']:
            checks['issues'].append({
                'severity': 'high',
                'message': 'SSL/TLS not configured in deployment files'
            })
        
        return checks
    
    def check_rate_limiting(self) -> Dict:
        """Check if rate limiting is implemented"""
        checks = {
            'implemented': False,
            'configuration': None,
            'issues': []
        }
        
        # Check for rate limiting in code
        rate_limit_files = ['telegram_bot.py', 'signal_api.py']
        for file_path in rate_limit_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'rate_limit' in content.lower() or 'ratelimit' in content.lower():
                        checks['implemented'] = True
                        break
        
        if not checks['implemented']:
            checks['issues'].append({
                'severity': 'medium',
                'message': 'Rate limiting not found in code'
            })
        
        return checks
    
    def check_gdpr_compliance(self) -> Dict:
        """Check GDPR compliance features"""
        compliance = {
            'privacy_policy': os.path.exists('PRIVACY_POLICY.md'),
            'terms_of_service': os.path.exists('TERMS_OF_SERVICE.md'),
            'data_export': False,
            'data_deletion': False,
            'cookie_consent': False,
            'issues': []
        }
        
        # Check for data export functionality
        if os.path.exists('user_manager.py'):
            with open('user_manager.py', 'r') as f:
                content = f.read()
                if 'export' in content.lower() or 'download' in content.lower():
                    compliance['data_export'] = True
        
        # Check for data deletion functionality
        if os.path.exists('database.py'):
            with open('database.py', 'r') as f:
                content = f.read()
                if 'delete' in content.lower() or 'remove' in content.lower():
                    compliance['data_deletion'] = True
        
        if not compliance['privacy_policy']:
            compliance['issues'].append({
                'severity': 'high',
                'message': 'Privacy Policy not found'
            })
        
        if not compliance['terms_of_service']:
            compliance['issues'].append({
                'severity': 'high',
                'message': 'Terms of Service not found'
            })
        
        return compliance
    
    def check_encryption(self) -> Dict:
        """Check encryption implementation"""
        encryption = {
            'at_rest': False,
            'in_transit': False,
            'key_management': False,
            'issues': []
        }
        
        # Check database encryption
        if os.path.exists('database.py'):
            with open('database.py', 'r') as f:
                content = f.read()
                if 'encrypt' in content.lower() or 'ssl' in content.lower():
                    encryption['at_rest'] = True
        
        # Check for HTTPS/TLS
        encryption['in_transit'] = self.check_ssl_configuration()['ssl_enabled']
        
        if not encryption['at_rest']:
            encryption['issues'].append({
                'severity': 'medium',
                'message': 'Database encryption at rest not verified'
            })
        
        if not encryption['in_transit']:
            encryption['issues'].append({
                'severity': 'high',
                'message': 'Encryption in transit (HTTPS/TLS) not configured'
            })
        
        return encryption
    
    def check_dependencies(self) -> Dict:
        """Check for known security vulnerabilities in dependencies"""
        vulnerabilities = {
            'checked': False,
            'vulnerable_packages': [],
            'outdated_packages': [],
            'issues': []
        }
        
        if os.path.exists('requirements.txt'):
            vulnerabilities['checked'] = True
            # Note: In production, use tools like safety, pip-audit, or Snyk
            vulnerabilities['issues'].append({
                'severity': 'info',
                'message': 'Run: pip install safety && safety check to scan for vulnerabilities'
            })
        
        return vulnerabilities
    
    def run_full_audit(self) -> Dict:
        """Run complete security audit"""
        logger.info("Starting security audit...")
        
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'environment_variables': self.check_environment_variables(),
            'ssl_configuration': self.check_ssl_configuration(),
            'rate_limiting': self.check_rate_limiting(),
            'gdpr_compliance': self.check_gdpr_compliance(),
            'encryption': self.check_encryption(),
            'dependencies': self.check_dependencies(),
            'summary': {
                'total_issues': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0
            }
        }
        
        # Calculate summary
        all_issues = []
        all_issues.extend(audit_results['environment_variables'])
        all_issues.extend(audit_results['ssl_configuration']['issues'])
        all_issues.extend(audit_results['rate_limiting']['issues'])
        all_issues.extend(audit_results['gdpr_compliance']['issues'])
        all_issues.extend(audit_results['encryption']['issues'])
        all_issues.extend(audit_results['dependencies']['issues'])
        
        for issue in all_issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                audit_results['summary']['high_severity'] += 1
            elif severity == 'medium':
                audit_results['summary']['medium_severity'] += 1
            else:
                audit_results['summary']['low_severity'] += 1
        
        audit_results['summary']['total_issues'] = len(all_issues)
        
        return audit_results
    
    def generate_report(self, audit_results: Dict) -> str:
        """Generate human-readable security audit report"""
        report = []
        report.append("=" * 70)
        report.append("SECURITY AUDIT REPORT")
        report.append("=" * 70)
        report.append(f"Date: {audit_results['timestamp']}")
        report.append("")
        
        # Summary
        summary = audit_results['summary']
        report.append("SUMMARY")
        report.append("-" * 70)
        report.append(f"Total Issues: {summary['total_issues']}")
        report.append(f"  High Severity: {summary['high_severity']}")
        report.append(f"  Medium Severity: {summary['medium_severity']}")
        report.append(f"  Low Severity: {summary['low_severity']}")
        report.append("")
        
        # Environment Variables
        env_issues = audit_results['environment_variables']
        if env_issues:
            report.append("ENVIRONMENT VARIABLES")
            report.append("-" * 70)
            for issue in env_issues:
                report.append(f"  [HIGH] {issue['file']}:{issue['line']} - Potential hardcoded secret")
            report.append("")
        
        # SSL Configuration
        ssl = audit_results['ssl_configuration']
        if ssl['issues']:
            report.append("SSL/TLS CONFIGURATION")
            report.append("-" * 70)
            for issue in ssl['issues']:
                report.append(f"  [{issue['severity'].upper()}] {issue['message']}")
            report.append("")
        
        # GDPR Compliance
        gdpr = audit_results['gdpr_compliance']
        if gdpr['issues']:
            report.append("GDPR COMPLIANCE")
            report.append("-" * 70)
            for issue in gdpr['issues']:
                report.append(f"  [{issue['severity'].upper()}] {issue['message']}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 70)
        if summary['high_severity'] > 0:
            report.append("  ⚠️  Address high-severity issues immediately")
        if summary['medium_severity'] > 0:
            report.append("  ⚠️  Review and fix medium-severity issues")
        report.append("  ✅ Run: pip install safety && safety check")
        report.append("  ✅ Configure SSL/TLS certificates")
        report.append("  ✅ Implement rate limiting")
        report.append("  ✅ Create Privacy Policy and Terms of Service")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)

def main():
    """Run security audit"""
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()
    
    # Print report
    report = auditor.generate_report(results)
    print(report)
    
    # Save results
    with open('security_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Security audit complete!")
    print("   Results saved to: security_audit_results.json")
    
    # Exit with error code if high severity issues found
    if results['summary']['high_severity'] > 0:
        exit(1)

if __name__ == "__main__":
    main()
