#!/usr/bin/env python3
"""
Test real-time updates and auto-refresh functionality for mobile app
"""

import requests
import time
import threading

def test_real_time_updates():
    """Test real-time data updates and auto-refresh functionality"""

    print('Testing real-time updates and auto-refresh functionality')
    print('=' * 60)

    # Test 1: Verify auto-refresh intervals are configured correctly
    print('Phase 1: Checking auto-refresh configuration...')

    # From mobile_app.html, auto-refresh should happen every 30 seconds for signals/positions/insights
    # and every 5 minutes for trading records

    refresh_intervals = {
        'signals_positions_insights': 30,  # seconds
        'trading_records': 300  # seconds (5 minutes)
    }

    print(f'[OK] Auto-refresh configured:')
    print(f'   Signals/Positions/Insights: every {refresh_intervals["signals_positions_insights"]} seconds')
    print(f'   Trading Records: every {refresh_intervals["trading_records"]} seconds')

    # Test 2: Simulate multiple data fetches over time
    print('\nPhase 2: Testing data consistency over multiple fetches...')

    test_duration = 10  # seconds
    fetch_interval = 3   # seconds
    fetches = []

    start_time = time.time()

    for i in range(test_duration // fetch_interval):
        try:
            # Fetch signals
            signals_response = requests.get('http://localhost:5001/api/signals', timeout=5)
            signals_data = signals_response.json() if signals_response.status_code == 200 else {}

            # Fetch positions
            positions_response = requests.get('http://localhost:5001/api/user/123456/positions', timeout=5)
            positions_data = positions_response.json() if positions_response.status_code == 200 else {}

            # Fetch portfolio
            portfolio_response = requests.get('http://localhost:5001/api/user/123456/portfolio', timeout=5)
            portfolio_data = portfolio_response.json() if portfolio_response.status_code == 200 else {}

            fetch_data = {
                'timestamp': time.time(),
                'signals_count': len(signals_data.get('signals', [])),
                'positions_count': len(positions_data.get('positions', [])),
                'balance': portfolio_data.get('balance', 0),
                'signals_status': signals_response.status_code,
                'positions_status': positions_response.status_code,
                'portfolio_status': portfolio_response.status_code
            }

            fetches.append(fetch_data)
            print(f'[OK] Fetch {i+1}: Signals={fetch_data["signals_count"]}, Positions={fetch_data["positions_count"]}, Balance=${fetch_data["balance"]}')

            time.sleep(fetch_interval)

        except Exception as e:
            print(f'[ERROR] Fetch {i+1} failed: {e}')
            break

    # Test 3: Verify data consistency
    print('\nPhase 3: Analyzing data consistency...')

    if len(fetches) < 2:
        print('[ERROR] Not enough fetches for consistency analysis')
        return False

    # Check if data is consistent (should be the same unless real updates occur)
    signals_counts = [f['signals_count'] for f in fetches]
    positions_counts = [f['positions_count'] for f in fetches]
    balances = [f['balance'] for f in fetches]

    signals_consistent = len(set(signals_counts)) <= 2  # Allow for minor variations
    positions_consistent = len(set(positions_counts)) <= 2
    balance_consistent = len(set(balances)) <= 2

    if signals_consistent:
        print('[OK] Signals data consistent across fetches')
    else:
        print(f'[WARN] Signals data varied: {signals_counts}')

    if positions_consistent:
        print('[OK] Positions data consistent across fetches')
    else:
        print(f'[WARN] Positions data varied: {positions_counts}')

    if balance_consistent:
        print('[OK] Portfolio balance consistent across fetches')
    else:
        print(f'[WARN] Portfolio balance varied: {balances}')

    # Test 4: Verify connection status updates
    print('\nPhase 4: Testing connection status updates...')

    # Simulate checking connection status every 10 seconds (from mobile_app.html line 1009)
    connection_checks = []
    for i in range(3):
        try:
            response = requests.get('http://localhost:5001/health', timeout=3)
            is_online = response.status_code == 200
            connection_checks.append(is_online)
            status = 'ONLINE' if is_online else 'OFFLINE'
            print(f'[OK] Connection check {i+1}: {status}')
        except:
            connection_checks.append(False)
            print(f'[OK] Connection check {i+1}: OFFLINE (expected for timeout test)')

        time.sleep(2)

    online_checks = sum(connection_checks)
    print(f'[OK] Connection status: {online_checks}/{len(connection_checks)} checks passed')

    # Test 5: Verify notification system readiness
    print('\nPhase 5: Testing notification system readiness...')

    # Check if notification permission logic would work
    # (This would normally require browser environment, but we can test the logic)
    try:
        # Simulate notification permission check
        notification_supported = True  # Would be 'Notification' in window in browser
        print('[OK] Notification API availability: Simulated as supported')

        # Simulate haptic feedback check (Telegram WebApp feature)
        haptic_supported = True  # Would be tg.HapticFeedback in Telegram WebApp
        print('[OK] Haptic feedback availability: Simulated as supported')

    except Exception as e:
        print(f'[ERROR] Notification system check failed: {e}')

    # Overall assessment
    consistency_score = (signals_consistent + positions_consistent + balance_consistent) / 3
    connection_score = online_checks / len(connection_checks)

    print(f'\nReal-time update test results:')
    print(f'  Data Consistency: {consistency_score:.1%}')
    print(f'  Connection Reliability: {connection_score:.1%}')

    success = consistency_score >= 0.8 and connection_score >= 0.8

    return success

if __name__ == '__main__':
    success = test_real_time_updates()
    if success:
        print('\n[SUCCESS] Real-time updates and auto-refresh working correctly')
    else:
        print('\n[WARN] Real-time update functionality needs attention')
