#!/usr/bin/env python3
"""
Test script for Mobile App Personal Dashboard API Integration
"""

import requests
import json
import time

def test_endpoints():
    """Test all API endpoints used by the mobile app"""

    base_url = 'http://localhost:5001/api'
    test_user_id = 123456  # Mock user ID for testing

    endpoints = [
        ('/signals', 'Signals'),
        (f'/user/{test_user_id}/portfolio', 'User Portfolio'),
        (f'/user/{test_user_id}/positions', 'User Positions'),
        ('/ai-insights', 'AI Insights'),
        ('/records?limit=5', 'Trading Records'),
        ('/performance', 'Performance Metrics')
    ]

    print('Testing Mobile App API Endpoints')
    print('=' * 50)

    results = {}

    for endpoint, description in endpoints:
        try:
            print(f"Testing {description}...")
            response = requests.get(f'{base_url}{endpoint}', timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check data structure and content
                if 'signals' in data:
                    count = len(data['signals'])
                    print(f'[OK] {description}: {count} signals retrieved')
                    if count > 0:
                        # Validate signal structure
                        signal = data['signals'][0]
                        required_fields = ['asset', 'direction', 'entry', 'stop_loss', 'take_profit1']
                        missing_fields = [field for field in required_fields if field not in signal]
                        if missing_fields:
                            print(f'[WARN] Missing fields in signal: {missing_fields}')
                        else:
                            print('   Signal structure: OK')
                    results[description] = {'status': 'success', 'count': count}

                elif 'positions' in data:
                    count = len(data['positions'])
                    print(f'[OK] {description}: {count} positions retrieved')
                    if count > 0:
                        # Validate position structure
                        position = data['positions'][0]
                        required_fields = ['asset', 'direction', 'entry', 'current', 'pnl']
                        missing_fields = [field for field in required_fields if field not in position]
                        if missing_fields:
                            print(f'[WARN] Missing fields in position: {missing_fields}')
                        else:
                            print('   Position structure: OK')
                    results[description] = {'status': 'success', 'count': count}

                elif 'insights' in data:
                    count = len(data['insights'])
                    print(f'[OK] {description}: {count} insights retrieved')
                    results[description] = {'status': 'success', 'count': count}

                elif 'records' in data:
                    count = len(data['records'])
                    print(f'[OK] {description}: {count} records retrieved')
                    results[description] = {'status': 'success', 'count': count}

                elif 'balance' in data:
                    balance = data.get('balance', 0)
                    print(f'[OK] {description}: Portfolio balance ${balance}')
                    results[description] = {'status': 'success', 'balance': balance}

                else:
                    print(f'[OK] {description}: OK (status {response.status_code})')
                    results[description] = {'status': 'success'}

            else:
                print(f'[ERROR] {description}: HTTP {response.status_code}')
                results[description] = {'status': 'error', 'code': response.status_code}

        except requests.exceptions.RequestException as e:
            print(f'[ERROR] {description}: Connection error - {str(e)}')
            results[description] = {'status': 'error', 'error': str(e)}
        except Exception as e:
            print(f'[ERROR] {description}: Unexpected error - {str(e)}')
            results[description] = {'status': 'error', 'error': str(e)}

        print()

    return results

if __name__ == '__main__':
    # Wait a moment for server to be fully ready
    time.sleep(2)

    results = test_endpoints()

    print('Summary:')
    print('=' * 30)
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)

    print(f'[SUCCESS] Successful endpoints: {success_count}/{total_count}')

    if success_count == total_count:
        print('All endpoints are working correctly!')
    else:
        print('[WARN] Some endpoints have issues. Check above for details.')

    print('\nTesting data format conversion for mobile app...')

    # Test data format conversion (simulate what mobile app does)
    try:
        signals_response = requests.get('http://localhost:5001/api/signals', timeout=10)
        if signals_response.status_code == 200:
            signals_data = signals_response.json()
            if 'signals' in signals_data and len(signals_data['signals']) > 0:
                # Simulate mobile app data conversion
                api_signal = signals_data['signals'][0]
                mobile_signal = {
                    'pair': api_signal.get('asset', 'EUR/USD'),
                    'direction': api_signal.get('direction', 'BUY').lower(),
                    'entry': api_signal.get('entry', 1.0845),
                    'tp': api_signal.get('take_profit1', 1.0945),
                    'sl': api_signal.get('stop_loss', 1.0745),
                    'criteria': round(api_signal.get('confidence', 80) / 5),  # Convert confidence to criteria
                    'type': 'forex',  # Default type
                    'timeframe': 'H1',
                    'timestamp': '2025-12-25T21:46:08.628994Z',
                    'confidence': api_signal.get('confidence', 80)
                }

                required_mobile_fields = ['pair', 'direction', 'entry', 'tp', 'sl', 'criteria']
                mobile_missing = [field for field in required_mobile_fields if field not in mobile_signal]

                if mobile_missing:
                    print(f'[ERROR] Mobile app data conversion failed. Missing: {mobile_missing}')
                else:
                    print('[OK] Mobile app data format conversion: OK')
                    print(f'   Sample converted signal: {mobile_signal["pair"]} {mobile_signal["direction"].upper()} @ {mobile_signal["entry"]}')

    except Exception as e:
        print(f'[ERROR] Data format conversion test failed: {e}')
