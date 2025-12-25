#!/usr/bin/env python3
"""
Comprehensive Bot Verification Script
Tests: Telegram API, Network, Runtime Errors, Database
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        if sys.stdout and not sys.stdout.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr and not sys.stderr.closed:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes for output (simplified for Windows compatibility)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    try:
        print(f"{GREEN}[OK]{RESET} {msg}")
    except:
        print(f"[OK] {msg}")

def print_error(msg):
    try:
        print(f"{RED}[FAIL]{RESET} {msg}")
    except:
        print(f"[FAIL] {msg}")

def print_warning(msg):
    try:
        print(f"{YELLOW}[!]{RESET} {msg}")
    except:
        print(f"[!] {msg}")

def print_info(msg):
    try:
        print(f"{BLUE}[*]{RESET} {msg}")
    except:
        print(f"[*] {msg}")

def print_section(title):
    try:
        print(f"\n{'='*60}")
        print(f"{BLUE}{title}{RESET}")
        print('='*60)
    except:
        print(f"\n{'='*60}")
        print(title)
        print('='*60)

# ============================================================================
# 1. VERIFY TELEGRAM API TOKEN AND BOT CONFIGURATION
# ============================================================================

def verify_telegram_token():
    """Verify Telegram API token and bot configuration"""
    print_section("1. VERIFYING TELEGRAM API TOKEN & CONFIGURATION")
    
    results = {
        'token_exists': False,
        'token_valid': False,
        'bot_info': None,
        'config_loaded': False,
        'errors': []
    }
    
    try:
        # Check if bot_config.py exists
        if not os.path.exists('bot_config.py'):
            results['errors'].append("bot_config.py not found")
            print_error("bot_config.py not found")
            return results
        
        print_success("bot_config.py found")
        results['config_loaded'] = True
        
        # Import bot config
        try:
            from bot_config import BOT_TOKEN, ALERT_ENABLED, CHECK_INTERVAL
            print_success("Configuration imported successfully")
            
            # Check if token is set
            if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
                results['errors'].append("BOT_TOKEN not set in bot_config.py")
                print_error("BOT_TOKEN not set")
                return results
            
            results['token_exists'] = True
            print_success(f"BOT_TOKEN found (length: {len(BOT_TOKEN)} chars)")
            
            # Validate token format (should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
            if ':' not in BOT_TOKEN:
                results['errors'].append("BOT_TOKEN format invalid (missing ':')")
                print_error("BOT_TOKEN format invalid")
                return results
            
            token_parts = BOT_TOKEN.split(':')
            if len(token_parts) != 2:
                results['errors'].append("BOT_TOKEN format invalid")
                print_error("BOT_TOKEN format invalid")
                return results
            
            print_success("BOT_TOKEN format valid")
            
            # Test token by calling Telegram API
            print_info("Testing token with Telegram API...")
            api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            
            try:
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        results['bot_info'] = bot_info
                        results['token_valid'] = True
                        print_success(f"Token is VALID!")
                        print_info(f"Bot Username: @{bot_info.get('username', 'N/A')}")
                        print_info(f"Bot Name: {bot_info.get('first_name', 'N/A')}")
                        print_info(f"Bot ID: {bot_info.get('id', 'N/A')}")
                        print_info(f"Is Bot: {bot_info.get('is_bot', 'N/A')}")
                    else:
                        error_desc = data.get('description', 'Unknown error')
                        results['errors'].append(f"Telegram API error: {error_desc}")
                        print_error(f"Token validation failed: {error_desc}")
                else:
                    results['errors'].append(f"HTTP {response.status_code}: {response.text}")
                    print_error(f"HTTP {response.status_code} error")
                    
            except requests.exceptions.Timeout:
                results['errors'].append("Telegram API timeout")
                print_error("Telegram API timeout (network issue)")
            except requests.exceptions.ConnectionError:
                results['errors'].append("Cannot connect to Telegram API")
                print_error("Cannot connect to Telegram API (network issue)")
            except Exception as e:
                results['errors'].append(f"API test error: {str(e)}")
                print_error(f"API test error: {str(e)}")
            
            # Check other config values
            print_info(f"ALERT_ENABLED: {ALERT_ENABLED}")
            print_info(f"CHECK_INTERVAL: {CHECK_INTERVAL} seconds")
            
        except ImportError as e:
            results['errors'].append(f"Import error: {str(e)}")
            print_error(f"Failed to import config: {str(e)}")
            
    except Exception as e:
        results['errors'].append(f"Unexpected error: {str(e)}")
        print_error(f"Unexpected error: {str(e)}")
    
    return results

# ============================================================================
# 2. TEST NETWORK CONNECTIVITY TO TELEGRAM API
# ============================================================================

def test_network_connectivity():
    """Test network connectivity to Telegram API"""
    print_section("2. TESTING NETWORK CONNECTIVITY TO TELEGRAM API")
    
    results = {
        'telegram_api_reachable': False,
        'dns_resolution': False,
        'response_time': None,
        'errors': []
    }
    
    try:
        # Test DNS resolution
        print_info("Testing DNS resolution for api.telegram.org...")
        import socket
        
        try:
            socket.gethostbyname('api.telegram.org')
            results['dns_resolution'] = True
            print_success("DNS resolution successful")
        except socket.gaierror as e:
            results['errors'].append(f"DNS resolution failed: {str(e)}")
            print_error(f"DNS resolution failed: {str(e)}")
            return results
        
        # Test HTTP connectivity
        print_info("Testing HTTP connectivity to Telegram API...")
        start_time = time.time()
        
        try:
            response = requests.get('https://api.telegram.org/bot123456789:test/getMe', timeout=10)
            elapsed = time.time() - start_time
            results['response_time'] = elapsed * 1000  # Convert to ms
            
            if response.status_code in [200, 401, 404]:  # 401/404 means API is reachable
                results['telegram_api_reachable'] = True
                print_success(f"Telegram API is reachable (response time: {results['response_time']:.0f}ms)")
            else:
                results['errors'].append(f"Unexpected status code: {response.status_code}")
                print_warning(f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            results['errors'].append("Connection timeout")
            print_error("Connection timeout (>10s)")
        except requests.exceptions.ConnectionError as e:
            results['errors'].append(f"Connection error: {str(e)}")
            print_error(f"Connection error: {str(e)}")
        except Exception as e:
            results['errors'].append(f"Network test error: {str(e)}")
            print_error(f"Network test error: {str(e)}")
            
    except Exception as e:
        results['errors'].append(f"Unexpected error: {str(e)}")
        print_error(f"Unexpected error: {str(e)}")
    
    return results

# ============================================================================
# 3. CHECK FOR RUNTIME EXCEPTIONS AND ERRORS IN BOT CODE
# ============================================================================

def check_runtime_errors():
    """Check for runtime exceptions and errors in bot code"""
    print_section("3. CHECKING FOR RUNTIME EXCEPTIONS & ERRORS")
    
    results = {
        'modules_imported': [],
        'modules_failed': [],
        'initialization_errors': [],
        'errors': []
    }
    
    # List of critical modules to test
    critical_modules = [
        ('telegram_bot', 'telegram_bot'),
        ('user_manager', 'user_manager'),
        ('database', 'database'),
        ('monitoring', 'monitoring'),
        ('payment_handler', 'payment_handler'),
        ('signal_api', 'signal_api'),
        ('tradingview_data_client', 'tradingview_data_client'),
    ]
    
    print_info("Testing critical module imports...")
    
    for module_name, import_name in critical_modules:
        try:
            print_info(f"Importing {module_name}...")
            module = __import__(import_name)
            results['modules_imported'].append(module_name)
            print_success(f"{module_name} imported successfully")
        except ImportError as e:
            results['modules_failed'].append(f"{module_name}: ImportError - {str(e)}")
            print_error(f"{module_name} import failed: {str(e)}")
        except SyntaxError as e:
            results['modules_failed'].append(f"{module_name}: SyntaxError - {str(e)}")
            print_error(f"{module_name} syntax error: {str(e)}")
        except Exception as e:
            results['modules_failed'].append(f"{module_name}: {type(e).__name__} - {str(e)}")
            print_error(f"{module_name} error: {type(e).__name__} - {str(e)}")
    
    # Test initialization of key classes
    print_info("\nTesting class initialization...")
    
    try:
        from user_manager import UserManager
        user_mgr = UserManager()
        print_success("UserManager initialized")
    except Exception as e:
        results['initialization_errors'].append(f"UserManager: {str(e)}")
        print_error(f"UserManager initialization failed: {str(e)}")
    
    try:
        from monitoring import get_logger
        logger = get_logger()
        print_success("Logger initialized")
    except Exception as e:
        results['initialization_errors'].append(f"Logger: {str(e)}")
        print_error(f"Logger initialization failed: {str(e)}")
    
    try:
        from database import Database
        db = Database()
        print_success("Database initialized")
    except Exception as e:
        results['initialization_errors'].append(f"Database: {str(e)}")
        print_error(f"Database initialization failed: {str(e)}")
    
    # Check for common syntax errors in telegram_bot.py
    print_info("\nChecking telegram_bot.py for syntax errors...")
    try:
        with open('telegram_bot.py', 'r', encoding='utf-8') as f:
            compile(f.read(), 'telegram_bot.py', 'exec')
        print_success("telegram_bot.py syntax is valid")
    except SyntaxError as e:
        results['errors'].append(f"telegram_bot.py syntax error: {str(e)}")
        print_error(f"telegram_bot.py syntax error: {str(e)}")
    except Exception as e:
        results['errors'].append(f"telegram_bot.py check error: {str(e)}")
        print_error(f"telegram_bot.py check error: {str(e)}")
    
    return results

# ============================================================================
# 4. VERIFY DATABASE CONNECTIONS AND OPERATIONS
# ============================================================================

def verify_database():
    """Verify database connections and operations"""
    print_section("4. VERIFYING DATABASE CONNECTIONS & OPERATIONS")
    
    results = {
        'database_file_exists': False,
        'users_file_exists': False,
        'database_readable': False,
        'database_writable': False,
        'operations_tested': False,
        'errors': []
    }
    
    try:
        # Check if database.py exists
        if os.path.exists('database.py'):
            print_success("database.py found")
        else:
            results['errors'].append("database.py not found")
            print_error("database.py not found")
            return results
        
        # Test database import and initialization
        try:
            from database import Database
            db = Database()
            print_success("Database class imported and initialized")
        except Exception as e:
            results['errors'].append(f"Database initialization failed: {str(e)}")
            print_error(f"Database initialization failed: {str(e)}")
            return results
        
        # Check for users_data.json (UserManager database)
        users_file = 'users_data.json'
        if os.path.exists(users_file):
            results['users_file_exists'] = True
            print_success(f"{users_file} exists")
            
            # Test reading
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                results['database_readable'] = True
                print_success(f"{users_file} is readable")
                print_info(f"Users in database: {len(data)}")
            except json.JSONDecodeError as e:
                results['errors'].append(f"{users_file} JSON decode error: {str(e)}")
                print_error(f"{users_file} JSON decode error: {str(e)}")
            except Exception as e:
                results['errors'].append(f"{users_file} read error: {str(e)}")
                print_error(f"{users_file} read error: {str(e)}")
            
            # Test writing
            try:
                test_data = {'test': 'write_test', 'timestamp': datetime.now().isoformat()}
                backup_file = f"{users_file}.backup_test"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f)
                os.remove(backup_file)
                results['database_writable'] = True
                print_success(f"{users_file} is writable")
            except Exception as e:
                results['errors'].append(f"{users_file} write error: {str(e)}")
                print_error(f"{users_file} write error: {str(e)}")
        else:
            print_warning(f"{users_file} not found (will be created on first use)")
        
        # Test UserManager operations
        try:
            from user_manager import UserManager
            um = UserManager()
            
            # Test get_user (should work even if file doesn't exist)
            test_user_id = 999999999
            user = um.get_user(test_user_id)
            if user:
                print_success("UserManager.get_user() works")
                results['operations_tested'] = True
            else:
                results['errors'].append("UserManager.get_user() returned None")
                print_error("UserManager.get_user() returned None")
            
            # Test has_feature_access
            access = um.has_feature_access(test_user_id, 'all_assets')
            print_success(f"UserManager.has_feature_access() works (result: {access})")
            
        except Exception as e:
            results['errors'].append(f"UserManager operations failed: {str(e)}")
            print_error(f"UserManager operations failed: {str(e)}")
        
        # Check for other database files
        db_files = ['signals_db.json', 'paper_trading.json', 'community_data.json']
        for db_file in db_files:
            if os.path.exists(db_file):
                print_info(f"{db_file} exists")
            else:
                print_info(f"{db_file} not found (optional)")
        
    except Exception as e:
        results['errors'].append(f"Unexpected error: {str(e)}")
        print_error(f"Unexpected error: {str(e)}")
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all verification tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}COMPREHENSIVE BOT VERIFICATION{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = {}
    
    # Run all tests
    all_results['telegram_token'] = verify_telegram_token()
    all_results['network'] = test_network_connectivity()
    all_results['runtime'] = check_runtime_errors()
    all_results['database'] = verify_database()
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    total_tests = 0
    passed_tests = 0
    
    # Telegram Token
    if all_results['telegram_token']['token_valid']:
        print_success("Telegram API Token: VALID")
        passed_tests += 1
    else:
        print_error("Telegram API Token: INVALID or NOT TESTED")
    total_tests += 1
    
    # Network
    if all_results['network']['telegram_api_reachable']:
        print_success("Network Connectivity: OK")
        passed_tests += 1
    else:
        print_error("Network Connectivity: FAILED")
    total_tests += 1
    
    # Runtime
    if len(all_results['runtime']['modules_failed']) == 0:
        print_success("Runtime Errors: NONE")
        passed_tests += 1
    else:
        print_error(f"Runtime Errors: {len(all_results['runtime']['modules_failed'])} modules failed")
    total_tests += 1
    
    # Database
    if all_results['database']['operations_tested']:
        print_success("Database Operations: WORKING")
        passed_tests += 1
    else:
        print_error("Database Operations: FAILED")
    total_tests += 1
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print_success("ALL CHECKS PASSED! Bot is ready to run.")
        return 0
    else:
        print_warning(f"{total_tests - passed_tests} check(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

