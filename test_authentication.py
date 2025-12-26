#!/usr/bin/env python3
"""
Test user authentication for mobile app integration
"""

from user_management_service import authenticate_user, get_user_portfolio_data

def test_authentication():
    """Test user authentication and portfolio data retrieval"""

    print('Testing user authentication...')
    print('=' * 40)

    # Test authentication with a mock user
    test_telegram_id = 123456
    test_username = 'testuser'
    test_first_name = 'Test User'

    user = authenticate_user(test_telegram_id, test_username, test_first_name)

    if user:
        print(f'[OK] User authenticated: ID {user.id} (Telegram ID: {user.telegram_id})')

        # Test portfolio data retrieval
        portfolio_data = get_user_portfolio_data(user.id)
        if portfolio_data:
            print('[OK] Portfolio data retrieved')
            portfolio = portfolio_data.get('portfolio', {})
            performance = portfolio_data.get('performance', {})

            print(f'   Balance: ${portfolio.get("current_capital", 0)}')
            print(f'   Win Rate: {performance.get("win_rate", 0)}%')
            print(f'   Total Trades: {performance.get("total_trades", 0)}')

            # Check if required fields are present
            required_portfolio_fields = ['current_capital', 'total_pnl', 'active_positions']
            required_performance_fields = ['win_rate', 'total_trades']

            missing_portfolio = [f for f in required_portfolio_fields if f not in portfolio]
            missing_performance = [f for f in required_performance_fields if f not in performance]

            if missing_portfolio or missing_performance:
                print(f'[WARN] Missing fields - Portfolio: {missing_portfolio}, Performance: {missing_performance}')
            else:
                print('[OK] All required fields present')

            return True
        else:
            print('[WARN] No portfolio data found - will use mock data')
            return False
    else:
        print('[WARN] User authentication failed - will use mock data fallback')
        return False

if __name__ == '__main__':
    success = test_authentication()
    if success:
        print('\n[SUCCESS] Authentication working correctly')
    else:
        print('\n[WARN] Authentication using fallback/mock data')
