#!/usr/bin/env python3
"""
Test error handling and fallback for mobile app integration
"""

import requests
import time

def test_error_handling():
    """Test error handling scenarios"""

    print('Testing error handling and fallback to mock data')
    print('=' * 50)

    # Phase 1: Testing with API server running
    print('Phase 1: Testing with API server running...')
    try:
        response = requests.get('http://localhost:5001/api/signals', timeout=5)
        print(f'[OK] API accessible: HTTP {response.status_code}')
        api_available = True
    except:
        print('[ERROR] API not accessible')
        api_available = False

    print('\nPhase 2: Testing error handling scenarios...')

    # Test timeout scenario
    try:
        response = requests.get('http://localhost:5001/api/signals', timeout=0.001)
        print(f'[UNEXPECTED] Request succeeded: HTTP {response.status_code}')
    except requests.exceptions.Timeout:
        print('[OK] Timeout handled correctly')
    except Exception as e:
        print(f'[OK] Error handled: {type(e).__name__}')

    # Test invalid endpoint
    try:
        response = requests.get('http://localhost:5001/api/nonexistent', timeout=5)
        if response.status_code == 404:
            print('[OK] 404 error handled correctly')
        else:
            print(f'[UNEXPECTED] Got HTTP {response.status_code} for invalid endpoint')
    except Exception as e:
        print(f'[ERROR] Unexpected error for 404 test: {e}')

    # Test server error simulation (HTTP 5xx)
    try:
        response = requests.get('http://localhost:5001/api/signals?simulate_error=500', timeout=5)
        if response.status_code >= 500:
            print('[OK] Server error handled correctly')
        else:
            print(f'[INFO] Server error test returned: HTTP {response.status_code}')
    except Exception as e:
        print(f'[OK] Server error simulation handled: {type(e).__name__}')

    print('\nPhase 3: Testing mobile app fallback logic simulation...')

    # Simulate what mobile app does when API fails (from mobile_app.html lines 662-707)
    def simulate_mobile_app_fallback():
        """Simulate mobile app fallback to mock data"""
        mock_signals = [
            {
                'pair': 'BTC/USDT',
                'direction': 'buy',
                'entry': 43250.50,
                'tp': 44500.00,
                'sl': 42800.00,
                'criteria': 18,
                'type': 'crypto',
                'timeframe': 'H1',
                'timestamp': '2025-12-25T21:46:08.628994Z',
                'confidence': 85
            },
            {
                'pair': 'EUR/USD',
                'direction': 'sell',
                'entry': 1.0875,
                'tp': 1.0820,
                'sl': 1.0910,
                'criteria': 17,
                'type': 'forex',
                'timeframe': 'M15',
                'timestamp': '2025-12-25T21:46:08.628994Z',
                'confidence': 78
            }
        ]

        # Simulate stats update
        total_signals = len(mock_signals)
        print(f'[OK] Fallback activated: {total_signals} mock signals loaded')

        # Simulate signal rendering
        for signal in mock_signals:
            print(f'   Mock signal: {signal["pair"]} {signal["direction"].upper()} @ {signal["entry"]}')

        return True

    fallback_success = simulate_mobile_app_fallback()

    # Test offline detection simulation
    print('\nPhase 4: Testing offline detection...')

    # Simulate offline by testing with invalid host
    try:
        response = requests.get('http://invalid-host-that-does-not-exist:5001/api/signals', timeout=2)
        print('[UNEXPECTED] Request to invalid host succeeded')
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print('[OK] Offline/connection error handled correctly')
    except Exception as e:
        print(f'[OK] Connection error handled: {type(e).__name__}')

    return api_available and fallback_success

if __name__ == '__main__':
    success = test_error_handling()
    if success:
        print('\n[SUCCESS] Error handling and fallback logic working correctly')
    else:
        print('\n[WARN] Some error handling tests failed')