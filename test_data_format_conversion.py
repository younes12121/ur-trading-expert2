#!/usr/bin/env python3
"""
Test data format conversion for mobile app integration
"""

import requests
import json

def test_data_format_conversion():
    """Test the data format conversion that mobile app performs"""

    print('Testing data format conversion for mobile app')
    print('=' * 50)

    # Fetch signals from API
    try:
        response = requests.get('http://localhost:5001/api/signals', timeout=10)
        if response.status_code != 200:
            print(f'[ERROR] Failed to fetch signals: HTTP {response.status_code}')
            return False

        signals_data = response.json()
        api_signals = signals_data.get('signals', [])

        if not api_signals:
            print('[WARN] No signals available for conversion test')
            return True

        print(f'[OK] Retrieved {len(api_signals)} signals from API')

        # Simulate mobile app conversion logic (from mobile_app.html lines 466-478)
        converted_signals = []
        for signal in api_signals:
            mobile_signal = {
                'pair': signal.get('asset', 'EUR/USD'),
                'direction': signal.get('direction', 'BUY').lower(),
                'entry': signal.get('entry', 1.0845),
                'tp': signal.get('take_profit1', signal.get('entry', 1.0845) * 1.01),
                'sl': signal.get('stop_loss', signal.get('entry', 1.0845) * 0.995),
                'criteria': round(signal.get('confidence', 18) / 5),  # Convert confidence to criteria score
                'type': signal.get('category', 'forex') if signal.get('asset', '').endswith('/') else 'crypto',
                'timeframe': 'H1',
                'timestamp': '2025-12-25T21:46:08.628994Z',  # Would be dynamic in real app
                'confidence': signal.get('confidence', 18),
                'analysis': signal.get('analysis', f"AI detected {signal.get('direction', 'BUY')} opportunity with {round(signal.get('confidence', 18) / 5)} criteria met")
            }
            converted_signals.append(mobile_signal)

        print(f'[OK] Successfully converted {len(converted_signals)} signals')

        # Validate converted signal structure
        required_fields = ['pair', 'direction', 'entry', 'tp', 'sl', 'criteria', 'type', 'timeframe', 'timestamp']
        validation_passed = True

        for i, signal in enumerate(converted_signals[:3]):  # Test first 3 signals
            missing_fields = [field for field in required_fields if field not in signal]
            if missing_fields:
                print(f'[ERROR] Signal {i+1} missing fields: {missing_fields}')
                validation_passed = False
            else:
                print(f'[OK] Signal {i+1} structure valid: {signal["pair"]} {signal["direction"].upper()} @ {signal["entry"]} (criteria: {signal["criteria"]}/20)')

        # Test portfolio data conversion
        print('\nTesting portfolio data conversion...')
        portfolio_response = requests.get('http://localhost:5001/api/user/123456/portfolio', timeout=10)
        if portfolio_response.status_code == 200:
            portfolio_data = portfolio_response.json()

            # Simulate mobile app usage (from mobile_app.html lines 503-507)
            mobile_balance = float(portfolio_data.get('balance', 0))
            mobile_winrate = float(portfolio_data.get('win_rate', 0))
            mobile_positions = int(portfolio_data.get('active_positions', 0))
            mobile_pnl = float(portfolio_data.get('today_pnl', 0))

            print(f'[OK] Portfolio conversion: Balance ${mobile_balance}, Win Rate {mobile_winrate}%, Positions {mobile_positions}, P&L ${mobile_pnl}')
        else:
            print(f'[WARN] Portfolio data fetch failed: HTTP {portfolio_response.status_code}')

        # Test positions data conversion
        print('\nTesting positions data conversion...')
        positions_response = requests.get('http://localhost:5001/api/user/123456/positions', timeout=10)
        if positions_response.status_code == 200:
            positions_data = positions_response.json()
            positions = positions_data.get('positions', [])

            if positions:
                # Validate position structure matches mobile app expectations
                position = positions[0]
                required_position_fields = ['asset', 'direction', 'entry', 'current', 'pnl', 'pnl_percent', 'size']
                missing_pos_fields = [field for field in required_position_fields if field not in position]

                if missing_pos_fields:
                    print(f'[ERROR] Position missing fields: {missing_pos_fields}')
                    validation_passed = False
                else:
                    print(f'[OK] Position structure valid: {position["asset"]} {position["direction"]} @ {position["entry"]} (P&L: ${position["pnl"]})')
            else:
                print('[WARN] No positions available for validation')
        else:
            print(f'[WARN] Positions data fetch failed: HTTP {positions_response.status_code}')

        return validation_passed

    except Exception as e:
        print(f'[ERROR] Data format conversion test failed: {e}')
        return False

if __name__ == '__main__':
    success = test_data_format_conversion()
    if success:
        print('\n[SUCCESS] Data format conversion working correctly')
    else:
        print('\n[ERROR] Data format conversion has issues')
