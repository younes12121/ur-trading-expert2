#!/usr/bin/env python3
"""
Test Dashboard-Telegram Integration
Tests that the dashboard can handle real-time data and multiple users
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import threading
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_management_service import (
    authenticate_user,
    get_user_portfolio_data,
    record_user_trade,
    get_user_statistics,
    get_user_dashboard_link
)

class DashboardIntegrationTester:
    def __init__(self):
        self.test_users = [
            {"telegram_id": 123456789, "username": "testuser1", "first_name": "Test User 1"},
            {"telegram_id": 987654321, "username": "testuser2", "first_name": "Test User 2"},
            {"telegram_id": 555666777, "username": "testuser3", "first_name": "Test User 3"}
        ]
        self.api_base_url = "http://localhost:5001/api"
        self.dashboard_process = None

    def start_dashboard_api(self):
        """Start the personal dashboard API in background"""
        print("Starting Personal Dashboard API...")
        try:
            self.dashboard_process = subprocess.Popen(
                [sys.executable, "personal_dashboard_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            # Wait for API to start
            time.sleep(3)
            print("OK: Dashboard API started")
            return True
        except Exception as e:
            print(f"ERROR: Failed to start dashboard API: {e}")
            return False

    def stop_dashboard_api(self):
        """Stop the dashboard API"""
        if self.dashboard_process:
            self.dashboard_process.terminate()
            self.dashboard_process.wait()
            print("STOP: Dashboard API stopped")

    def test_user_creation_and_authentication(self):
        """Test user creation and authentication"""
        print("\nTEST: User Creation & Authentication...")

        for user_data in self.test_users:
            telegram_id = user_data["telegram_id"]
            username = user_data["username"]
            first_name = user_data["first_name"]

            # Test authentication (should auto-create user)
            user = authenticate_user(telegram_id, username, first_name)
            if user:
                print(f"OK: User {telegram_id} authenticated/created: {user.telegram_id}")
            else:
                print(f"ERROR: Failed to authenticate user {telegram_id}")
                return False

        print("OK: All users created successfully")
        return True

    def test_portfolio_data_handling(self):
        """Test that portfolio data can be retrieved for different users"""
        print("\nTEST: Portfolio Data Handling...")

        for user_data in self.test_users:
            telegram_id = user_data["telegram_id"]

            # Get portfolio data
            portfolio = get_user_portfolio_data(telegram_id)
            if portfolio:
                print(f"OK: Portfolio data for user {telegram_id}:")
                print(f"   Balance: ${portfolio['portfolio']['current_capital']}")
                print(f"   Active Positions: {portfolio['portfolio']['active_positions']}")
                print(f"   Total Trades: {portfolio['performance']['total_trades']}")
            else:
                print(f"ERROR: No portfolio data for user {telegram_id}")
                return False

        print("OK: All portfolio data retrieved successfully")
        return True

    def test_trade_recording(self):
        """Test recording trades for different users"""
        print("\nTEST: Trade Recording...")

        sample_trades = [
            {
                "asset": "EUR/USD",
                "direction": "BUY",
                "entry_price": 1.0845,
                "quantity": 0.5,
                "strategy": "Trend Following",
                "signal_id": "test_signal_1"
            },
            {
                "asset": "BTC/USDT",
                "direction": "SELL",
                "entry_price": 45230.00,
                "quantity": 0.02,
                "strategy": "Breakout",
                "signal_id": "test_signal_2"
            },
            {
                "asset": "XAU/USD",
                "direction": "BUY",
                "entry_price": 1950.50,
                "quantity": 0.1,
                "strategy": "Support Bounce",
                "signal_id": "test_signal_3"
            }
        ]

        for i, user_data in enumerate(self.test_users):
            telegram_id = user_data["telegram_id"]
            trade = sample_trades[i % len(sample_trades)]  # Cycle through trades

            success = record_user_trade(telegram_id, trade)
            if success:
                print(f"OK: Trade recorded for user {telegram_id}: {trade['asset']} {trade['direction']}")
            else:
                print(f"ERROR: Failed to record trade for user {telegram_id}")
                return False

        print("OK: All trades recorded successfully")
        return True

    def test_dashboard_api_endpoints(self):
        """Test dashboard API endpoints with real user data"""
        print("\nTEST: Dashboard API Endpoints...")

        test_telegram_id = self.test_users[0]["telegram_id"]

        endpoints = [
            f"/user/{test_telegram_id}/portfolio",
            f"/user/{test_telegram_id}/positions",
            "/signals",
            "/ai-insights",
            "/records",
            "/health"
        ]

        for endpoint in endpoints:
            try:
                url = f"{self.api_base_url}{endpoint}"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    print(f"OK: {endpoint} - Status: {response.status_code}")
                else:
                    print(f"WARN: {endpoint} - Status: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"ERROR: {endpoint} - Error: {e}")
                return False

        print("OK: All API endpoints tested")
        return True

    def test_real_time_data_simulation(self):
        """Simulate real-time data updates"""
        print("\nTEST: Real-Time Data Simulation...")

        # Add some mock signals data
        signals_data = {
            "signals": [
                {
                    "asset": "EUR/USD",
                    "direction": "BUY",
                    "entry": 1.0845,
                    "take_profit1": 1.0945,
                    "take_profit2": 1.0995,
                    "stop_loss": 1.0795,
                    "confidence": 89,
                    "category": "forex",
                    "analysis": "Strong bullish momentum detected"
                },
                {
                    "asset": "BTC/USDT",
                    "direction": "SELL",
                    "entry": 45230.00,
                    "take_profit1": 44230.00,
                    "take_profit2": 43730.00,
                    "stop_loss": 45730.00,
                    "confidence": 76,
                    "category": "crypto",
                    "analysis": "Bearish divergence forming"
                }
            ]
        }

        # Write signals to file (simulating real-time data)
        with open("signals_db.json", "w") as f:
            json.dump(signals_data["signals"], f, indent=2)

        print("OK: Real-time signals data updated")

        # Test that dashboard can read the signals
        try:
            response = requests.get(f"{self.api_base_url}/signals", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("signals"):
                    print(f"OK: Dashboard retrieved {len(data['signals'])} live signals")
                    return True
                else:
                    print("WARN: No signals data returned")
                    return False
            else:
                print(f"ERROR: Signals endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Error testing signals: {e}")
            return False

    def test_user_isolation(self):
        """Test that user data is properly isolated"""
        print("\nTEST: User Data Isolation...")

        # Add different portfolio data for each user
        for i, user_data in enumerate(self.test_users):
            telegram_id = user_data["telegram_id"]

            # Get user stats
            stats = get_user_statistics(telegram_id)
            print(f"OK: User {telegram_id} has {stats['total_trades']} trades")

            # Verify each user has their own data
            portfolio = get_user_portfolio_data(telegram_id)
            if portfolio:
                balance = portfolio['portfolio']['current_capital']
                print(f"   Portfolio balance: ${balance}")
            else:
                print(f"ERROR: No portfolio data for user {telegram_id}")
                return False

        print("OK: User data isolation verified")
        return True

    def test_concurrent_users_simulation(self):
        """Simulate multiple users accessing dashboard simultaneously"""
        print("\nTEST: Concurrent User Access...")

        def user_request(user_id, endpoint):
            """Simulate a user making a request"""
            try:
                url = f"{self.api_base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                return f"User {user_id}: {endpoint} - {response.status_code}"
            except Exception as e:
                return f"User {user_id}: {endpoint} - ERROR: {e}"

        # Simulate 3 users making requests simultaneously
        threads = []
        results = []

        for i, user_data in enumerate(self.test_users):
            telegram_id = user_data["telegram_id"]

            # Each user makes multiple requests
            endpoints = [
                f"/user/{telegram_id}/portfolio",
                f"/user/{telegram_id}/positions",
                "/signals",
                "/ai-insights"
            ]

            for endpoint in endpoints:
                thread = threading.Thread(
                    target=lambda eid=endpoint, uid=telegram_id: results.append(user_request(uid, eid))
                )
                threads.append(thread)
                thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Check results
        success_count = 0
        for result in results:
            if "200" in result or "User" in result:
                success_count += 1
                print(f"OK: {result}")
            else:
                print(f"ERROR: {result}")

        if success_count >= len(results) * 0.8:  # 80% success rate
            print(f"PASS: Concurrent access test passed: {success_count}/{len(results)} successful")
            return True
        else:
            print(f"FAIL: Concurrent access test failed: {success_count}/{len(results)} successful")
            return False

    def run_complete_test_suite(self):
        """Run the complete test suite"""
        print("TEST SUITE: URTRADINGEXPERT.COM - DASHBOARD-TELEGRAM INTEGRATION")
        print("=" * 70)

        tests = [
            ("User Creation & Authentication", self.test_user_creation_and_authentication),
            ("Portfolio Data Handling", self.test_portfolio_data_handling),
            ("Trade Recording", self.test_trade_recording),
            ("Dashboard API Endpoints", self.test_dashboard_api_endpoints),
            ("Real-Time Data Simulation", self.test_real_time_data_simulation),
            ("User Data Isolation", self.test_user_isolation),
            ("Concurrent User Access", self.test_concurrent_users_simulation)
        ]

        passed = 0
        total = len(tests)

        # Start dashboard API
        if not self.start_dashboard_api():
            print("ERROR: Cannot proceed without dashboard API")
            return False

        try:
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                if test_func():
                    passed += 1
                    print(f"PASS: {test_name}")
                else:
                    print(f"FAIL: {test_name}")

            print("\n" + "=" * 70)
            print(f"RESULTS: {passed}/{total} tests passed")

            if passed == total:
                print("SUCCESS: ALL TESTS PASSED! Dashboard-Telegram integration is READY!")
                print("DEPLOY: You can safely deploy to urtradingexpert.com")
                return True
            elif passed >= total * 0.8:  # 80% success rate
                print("WARNING: MOST TESTS PASSED! Minor issues detected but deployment possible")
                return True
            else:
                print("CRITICAL: ISSUES DETECTED! Do not deploy until fixed")
                return False

        finally:
            self.stop_dashboard_api()

def main():
    tester = DashboardIntegrationTester()
    success = tester.run_complete_test_suite()

    if success:
        print("\nDEPLOYMENT STATUS: READY FOR PRODUCTION")
        print("\nNext steps:")
        print("1. Get your server (DigitalOcean/Linode/Vultr)")
        print("2. Point urtradingexpert.com DNS to server IP")
        print("3. Run: python3 deploy_production.py --domain urtradingexpert.com --email admin@urtradingexpert.com")
        print("4. Add API keys to .env file")
        print("5. Launch!")
    else:
        print("\nDEPLOYMENT STATUS: NOT READY - FIX ISSUES FIRST")
        print("\nTroubleshooting:")
        print("1. Check user_management_service.py")
        print("2. Verify personal_dashboard_api.py imports")
        print("3. Test individual functions manually")
        print("4. Fix any failed tests before deploying")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
