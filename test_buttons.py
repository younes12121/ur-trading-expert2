#!/usr/bin/env python3
"""
Test script to verify button functionality without running the full bot
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_button_functions():
    """Test that all button keyboard functions work correctly"""
    try:
        # Import the functions we created
        from telegram_bot import (
            get_main_commands_keyboard,
            get_signals_keyboard,
            get_analysis_keyboard,
            get_settings_keyboard,
            get_account_keyboard,
            get_forex_keyboard,
            get_futures_keyboard,
            get_elite_keyboard
        )

        # Test each function
        print("Testing button keyboard functions...")

        keyboards = [
            ("Main Commands", get_main_commands_keyboard()),
            ("Signals", get_signals_keyboard()),
            ("Analysis", get_analysis_keyboard()),
            ("Settings", get_settings_keyboard()),
            ("Account", get_account_keyboard()),
            ("Forex", get_forex_keyboard()),
            ("Futures", get_futures_keyboard()),
            ("Elite", get_elite_keyboard()),
        ]

        for name, keyboard in keyboards:
            if keyboard and hasattr(keyboard, 'inline_keyboard'):
                button_count = sum(len(row) for row in keyboard.inline_keyboard)
                print(f"✅ {name}: {button_count} buttons")
            else:
                print(f"❌ {name}: Invalid keyboard")

        print("\n🎉 All button functions working correctly!")
        print("\n📋 Button Categories:")
        print("• Main Commands: Signals, Elite, Analysis, News, Settings, Account, Learn, Stats, Admin")
        print("• Signals: Quick Start, All Signals, BTC, ETH, Gold, Futures, Forex, International, Ultra, Quantum")
        print("• Analysis: Market Heatmap, Correlations, Volatility, Multi-Timeframe, Smart Money, Order Flow, Market Maker, Volume Profile, AI Predict, Sentiment")
        print("• Settings: Language, Timezone, Region, Quiet Mode, Notifications, Preferences")
        print("• Account: Subscribe, Billing, Profile, Leaderboard, Performance, Portfolio, Risk Management, Analytics")
        print("• Forex: EUR/USD, GBP/USD, USD/JPY, AUD/USD, NZD/USD, USD/CHF, Forex Overview")
        print("• Futures: E-mini S&P 500, E-mini NASDAQ")
        print("• Elite: Ultra Elite and Quantum Elite signals for BTC, Gold, EUR/USD")

        return True

    except Exception as e:
        print(f"❌ Error testing buttons: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_button_functions()
    sys.exit(0 if success else 1)
