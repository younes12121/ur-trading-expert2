#!/usr/bin/env python3
"""
Test script to verify the dashboard command logic works correctly
"""

import html

def test_dashboard_message():
    """Test the dashboard message generation logic"""

    # Simulate user data
    username = "test_user_123"
    first_name = "Test"
    telegram_id = 123456789
    dashboard_url = "https://example.com/dashboard?user=123"

    # Simulate portfolio data
    portfolio_data = {
        'portfolio': {
            'current_capital': 10000.50,
            'total_pnl': 1250.75,
            'total_pnl_pct': 12.5,
            'today_pnl': 45.20,
            'active_positions': 3,
            'capital_growth': 15.3
        },
        'performance': {
            'total_trades': 150,
            'win_rate': 68.5
        },
        'active_positions': [
            {'asset': 'EURUSD', 'direction': 'LONG', 'pnl': 125.50},
            {'asset': 'GBPUSD', 'direction': 'SHORT', 'pnl': -25.30},
            {'asset': 'USDJPY', 'direction': 'LONG', 'pnl': 89.75}
        ]
    }

    # Test the fixed logic
    account_name = username or first_name or f"ID: {telegram_id}"
    safe_account = account_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')

    safe_url = dashboard_url

    portfolio = portfolio_data.get('portfolio', {})
    performance = portfolio_data.get('performance', {})

    msg_lines = [
        "*📊 YOUR PERSONAL TRADING DASHBOARD*",
        "",
        f"👤 *Account:* {safe_account}",
        f"💰 *Current Capital:* ${portfolio.get('current_capital', 0):.2f}",
        f"📈 *Total P&L:* ${portfolio.get('total_pnl', 0):.2f} ({portfolio.get('total_pnl_pct', 0):.1f}%)",
        f"📊 *Today's P&L:* ${portfolio.get('today_pnl', 0):.2f}",
        "",
        "🎯 *Performance Metrics:*",
        f"• Total Trades: {performance.get('total_trades', 0)}",
        f"• Win Rate: {performance.get('win_rate', 0):.1f}%",
        f"• Active Positions: {portfolio.get('active_positions', 0)}",
        f"• Capital Growth: {portfolio.get('capital_growth', 0):.1f}%",
        "",
        f"🌐 *Web Dashboard:* {safe_url}",
        "",
        "💡 *Commands:*",
        "• /portfolio — Detailed portfolio view",
        "• /trades — Recent trade history",
        "• /stats — Performance statistics",
    ]
    msg = "\n".join(msg_lines)

    # Add active positions if any
    active_positions = portfolio_data.get('active_positions', [])
    if active_positions:
        msg += "\n\n📍 *Active Positions:*"
        for pos in active_positions[:3]:  # Show top 3
            pnl_color = "🟢" if pos['pnl'] >= 0 else "🔴"
            msg += f"\n{pnl_color} {html.escape(pos['asset'])} {html.escape(pos['direction'])} - P&L: ${pos['pnl']:.2f}"

    print("Generated dashboard message:")
    print("=" * 50)
    try:
        print(msg)
    except UnicodeEncodeError:
        print("(Message contains Unicode characters that can't be displayed in this terminal)")
        print(f"Message length: {len(msg)} characters")
    print("=" * 50)

    # Test for potential Markdown parsing issues
    print("\nTesting for Markdown entity issues...")

    # Check for unclosed asterisks
    asterisk_count = msg.count('*')
    if asterisk_count % 2 == 0:
        print("[OK] Asterisks are properly balanced")
    else:
        print(f"[ERROR] Unbalanced asterisks: {asterisk_count} found")

    # Check for problematic characters in account name
    problematic_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    has_problems = any(char in account_name for char in problematic_chars)
    if has_problems:
        print(f"[WARNING] Account name '{account_name}' contains special characters that were escaped")
    else:
        print(f"[OK] Account name '{account_name}' is safe for Markdown")

    return msg

if __name__ == "__main__":
    test_dashboard_message()
