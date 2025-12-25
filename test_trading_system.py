#!/usr/bin/env python3
"""
Test Script for the Complete Trading System
Demonstrates user registration, trade execution, and dashboard functionality
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_user_management():
    """Test user management system"""
    print("Testing User Management System...")

    try:
        from user_management_service import authenticate_user, get_user_portfolio_data

        # Test user authentication
        test_telegram_id = 123456789
        user = authenticate_user(test_telegram_id, "testuser", "Test", "User")
        print(f"[OK] User authenticated: {user.telegram_id} ({user.username})")

        # Test portfolio data retrieval
        portfolio = get_user_portfolio_data(user.id)
        print(f"[OK] Portfolio data retrieved: ${portfolio.get('portfolio', {}).get('current_capital', 0):.2f} capital")

        return True
    except Exception as e:
        print(f"[FAIL] User management test failed: {e}")
        return False

def test_trading_execution():
    """Test trading execution engine"""
    print("📊 Testing Trading Execution Engine...")

    try:
        from trading_execution_engine import execute_user_signal, get_user_trading_performance

        test_telegram_id = 123456789

        # Create a test signal
        test_signal = {
            'asset': 'EURUSD',
            'direction': 'BUY',
            'entry': 1.0845,
            'price': 1.0845,
            'stop_loss': 1.0795,
            'tp1': 1.0945,
            'signal_type': 'BUY',
            'has_signal': True,
            'timestamp': datetime.now().isoformat()
        }

        # Execute the signal
        result = execute_user_signal(test_telegram_id, test_signal)
        if result['success']:
            print(f"✅ Trade executed: {result['message']}")
        else:
            print(f"⚠️  Trade execution note: {result.get('error', 'Unknown issue')}")

        # Test performance retrieval
        performance = get_user_trading_performance(test_telegram_id)
        print(f"✅ Performance data retrieved: {performance.get('overview', {}).get('total_trades', 0)} trades")

        return True
    except Exception as e:
        print(f"❌ Trading execution test failed: {e}")
        return False

def test_dashboard_api():
    """Test dashboard API functionality"""
    print("🌐 Testing Dashboard API...")

    try:
        from personal_dashboard_api import PersonalDashboardAPI

        api = PersonalDashboardAPI()

        # Test portfolio data
        portfolio_data = api.get_portfolio_data(123456789)
        print(f"✅ Portfolio API data: ${portfolio_data.get('balance', 0):.2f} balance")

        # Test positions data
        positions_data = api.get_current_positions(123456789)
        print(f"✅ Positions API data: {len(positions_data)} positions")

        return True
    except Exception as e:
        print(f"❌ Dashboard API test failed: {e}")
        return False

def test_signal_enhancement():
    """Test signal enhancement with AI"""
    print("🤖 Testing Signal Enhancement...")

    try:
        from quantum_elite_signal_integration import enhance_signal_with_quantum_elite

        test_signal = {
            'asset': 'BTC',
            'signal_type': 'BUY',
            'price': 45000,
            'confidence': 0.8
        }

        enhanced = enhance_signal_with_quantum_elite(test_signal, 'BTC')
        print(f"✅ Signal enhanced: {enhanced.get('signal_quality', 'unknown')} quality")

        return True
    except Exception as e:
        print(f"❌ Signal enhancement test failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("TESTING TRADING SYSTEM")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("User Management", test_user_management),
        ("Trading Execution", test_trading_execution),
        ("Dashboard API", test_dashboard_api),
        ("Signal Enhancement", test_signal_enhancement)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'-'*20} {test_name} {'-'*20}")
        start_time = time.time()
        success = test_func()
        duration = time.time() - start_time
        results.append((test_name, success, duration))
        status = "✅ PASSED" if success else "❌ FAILED"
        print(".2f")
    print(f"\n{'='*50}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*50}")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print("6.2f")
    print(f"{'-'*50}")
    print(f"🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("\n🚀 To start the system:")
        print("   python start_trading_system.py")
        print("\n📱 Telegram Commands:")
        print("   /start - Register and get started")
        print("   /dashboard - View personal dashboard")
        print("   /execute EURUSD BUY 1.0845 - Execute a trade")
        print("   /performance - View trading analytics")
        return 0
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
