#!/usr/bin/env python3
"""
🚀 UR Trading Expert Bot - Startup Script
Easy launcher with environment check and status monitoring
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print startup banner"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("🚀 UR TRADING EXPERT BOT")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")

def check_python_version():
    """Verify Python version is 3.9+"""
    print(f"{Colors.OKBLUE}Checking Python version...{Colors.ENDC}")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"{Colors.FAIL}❌ Python 3.9+ required (you have {version.major}.{version.minor}){Colors.ENDC}")
        return False
    print(f"{Colors.OKGREEN}✅ Python {version.major}.{version.minor}.{version.micro}{Colors.ENDC}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print(f"\n{Colors.OKBLUE}Checking dependencies...{Colors.ENDC}")
    required_packages = [
        'telegram',
        'sqlalchemy',
        'stripe',
        'numpy',
        'pandas',
        'sklearn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"{Colors.OKGREEN}✅ {package}{Colors.ENDC}")
        except ImportError:
            print(f"{Colors.FAIL}❌ {package}{Colors.ENDC}")
            missing.append(package)
    
    if missing:
        print(f"\n{Colors.WARNING}Missing packages detected!{Colors.ENDC}")
        print(f"Run: {Colors.BOLD}pip install -r requirements.txt{Colors.ENDC}\n")
        return False
    
    return True

def check_config():
    """Verify configuration file exists"""
    print(f"\n{Colors.OKBLUE}Checking configuration...{Colors.ENDC}")
    
    if not Path('bot_config.py').exists():
        print(f"{Colors.FAIL}❌ bot_config.py not found{Colors.ENDC}")
        return False
    
    print(f"{Colors.OKGREEN}✅ bot_config.py found{Colors.ENDC}")
    
    # Check for bot token
    try:
        from bot_config import BOT_TOKEN
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
            print(f"{Colors.WARNING}⚠️  Bot token not configured{Colors.ENDC}")
            print(f"   Get your token from @BotFather on Telegram")
            return False
        print(f"{Colors.OKGREEN}✅ Bot token configured{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.FAIL}❌ Could not import BOT_TOKEN{Colors.ENDC}")
        return False
    
    return True

def check_modules():
    """Verify all core modules exist"""
    print(f"\n{Colors.OKBLUE}Checking core modules...{Colors.ENDC}")
    
    modules = [
        'telegram_bot.py',
        'educational_assistant.py',
        'notification_manager.py',
        'database.py',
        'user_manager.py',
        'payment_handler.py',
        'user_profiles.py',
        'leaderboard.py',
        'community_features.py',
        'referral_system.py',
        'broker_connector.py',
        'ml_predictor.py',
        'sentiment_analyzer.py',
        'signal_api.py',
        'trade_tracker.py'
    ]
    
    all_found = True
    for module in modules:
        if Path(module).exists():
            print(f"{Colors.OKGREEN}✅ {module}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ {module}{Colors.ENDC}")
            all_found = False
    
    return all_found

def show_menu():
    """Display startup menu"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Select Mode:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}1. 🚀 Start Bot (Standard Mode){Colors.ENDC}")
    print(f"{Colors.OKCYAN}2. 🐛 Start Bot (Debug Mode){Colors.ENDC}")
    print(f"{Colors.OKCYAN}3. 📊 Run Quick Test{Colors.ENDC}")
    print(f"{Colors.OKCYAN}4. 📈 View System Stats{Colors.ENDC}")
    print(f"{Colors.OKCYAN}5. 🔧 Check Configuration{Colors.ENDC}")
    print(f"{Colors.OKCYAN}6. ❌ Exit{Colors.ENDC}")
    
    choice = input(f"\n{Colors.BOLD}Enter your choice (1-6): {Colors.ENDC}")
    return choice

def start_bot(debug=False):
    """Start the Telegram bot"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Starting Bot...{Colors.ENDC}\n")
    print(f"{Colors.WARNING}Press Ctrl+C to stop the bot{Colors.ENDC}\n")
    time.sleep(1)
    
    try:
        if debug:
            # Set debug environment variable
            os.environ['DEBUG_MODE'] = 'true'
        
        # Run the bot
        subprocess.run([sys.executable, 'telegram_bot.py'], check=True)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Bot stopped by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error starting bot: {e}{Colors.ENDC}")

def run_test():
    """Run quick functionality test"""
    print(f"\n{Colors.HEADER}Running Quick Test...{Colors.ENDC}\n")
    try:
        subprocess.run([sys.executable, 'test_bot.py'], check=True)
    except FileNotFoundError:
        print(f"{Colors.WARNING}test_bot.py not found{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Test failed: {e}{Colors.ENDC}")

def show_stats():
    """Display system statistics"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}System Statistics:{Colors.ENDC}\n")
    
    # Count modules
    py_files = list(Path('.').glob('*.py'))
    print(f"📦 Python Modules: {len(py_files)}")
    
    # Check JSON data files
    json_files = list(Path('.').glob('*.json'))
    print(f"📁 Data Files: {len(json_files)}")
    
    # Check if bot is running
    print(f"\n{Colors.OKBLUE}Bot Status:{Colors.ENDC}")
    print(f"   Check Telegram: Send /start to your bot")
    print(f"   Admin ID: 7713994326")
    print(f"   Total Commands: 65+")
    print(f"   Trading Assets: 13")
    
    # Show features
    print(f"\n{Colors.OKGREEN}Active Features:{Colors.ENDC}")
    features = [
        "✅ Signal Generation (15 assets: BTC, Gold, ES, NQ, 11 Forex)",
        "✅ Educational Assistant (350+ items)",
        "✅ Smart Notifications",
        "✅ User Tiers & Monetization",
        "✅ Community Features",
        "✅ Leaderboards & Profiles",
        "✅ Referral System (20% commission)",
        "✅ Broker Integration (MT5/OANDA)",
        "✅ AI Predictions (ML)",
        "✅ Sentiment Analysis",
        "✅ Risk Management",
        "✅ Performance Analytics"
    ]
    for feature in features:
        print(f"   {feature}")

def main():
    """Main entry point"""
    print_header()
    
    # Run startup checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Core Modules", check_modules)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            break
    
    if not all_passed:
        print(f"\n{Colors.FAIL}Startup checks failed! Please fix the issues above.{Colors.ENDC}\n")
        sys.exit(1)
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ All checks passed! Bot is ready to launch.{Colors.ENDC}\n")
    
    # Show menu and handle choice
    while True:
        choice = show_menu()
        
        if choice == '1':
            start_bot(debug=False)
            break
        elif choice == '2':
            start_bot(debug=True)
            break
        elif choice == '3':
            run_test()
            input("\nPress Enter to continue...")
        elif choice == '4':
            show_stats()
            input("\nPress Enter to continue...")
        elif choice == '5':
            check_config()
            check_modules()
            input("\nPress Enter to continue...")
        elif choice == '6':
            print(f"\n{Colors.OKGREEN}Goodbye!{Colors.ENDC}\n")
            break
        else:
            print(f"\n{Colors.FAIL}Invalid choice. Please try again.{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}\n")
        sys.exit(0)


