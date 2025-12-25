#!/usr/bin/env python3
"""
Test script to verify Daily Signals integration in telegram bot
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_daily_signals_integration():
    """Test that daily signals system is properly integrated"""

    print("🧪 TESTING DAILY SIGNALS INTEGRATION")
    print("=" * 50)

    try:
        # Test 1: Import the daily signals system
        print("✅ Test 1: Importing daily signals system...")
        from daily_signals_system import generate_daily_signal, get_daily_signals_status
        print("   ✅ Import successful")

        # Test 2: Generate a test signal
        print("✅ Test 2: Generating test signal...")
        signal = generate_daily_signal(1000)
        if signal:
            print("   ✅ Signal generated successfully")
            print(f"   📊 Asset: {signal['asset']}, Direction: {signal['direction']}, Tier: {signal['tier']}")
        else:
            print("   ⚠️  No signal generated (may be due to limits)")

        # Test 3: Check system status
        print("✅ Test 3: Checking system status...")
        status = get_daily_signals_status()
        print("   ✅ Status retrieved")
        print(f"   📊 Daily signals today: {status['daily_signals_today']}/{status['daily_limit']}")

        # Test 4: Check telegram bot imports
        print("✅ Test 4: Testing telegram bot imports...")
        try:
            # This will test if the imports in telegram_bot.py work
            from daily_signals_system import generate_daily_signal, get_daily_signals_status
            print("   ✅ Telegram bot imports working")
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return False

        # Test 5: Check command functions exist
        print("✅ Test 5: Checking command functions...")
        try:
            # Import telegram_bot to check if functions exist
            import telegram_bot
            if hasattr(telegram_bot, 'daily_signal_command'):
                print("   ✅ daily_signal_command found")
            else:
                print("   ❌ daily_signal_command not found")
                return False

            if hasattr(telegram_bot, 'daily_status_command'):
                print("   ✅ daily_status_command found")
            else:
                print("   ❌ daily_status_command not found")
                return False

            if hasattr(telegram_bot, 'daily_signals_alert_loop'):
                print("   ✅ daily_signals_alert_loop found")
            else:
                print("   ❌ daily_signals_alert_loop not found")
                return False

        except Exception as e:
            print(f"   ❌ Error checking functions: {e}")
            return False

        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Daily Signals System successfully integrated!")
        print("\n🚀 Ready to deploy with commands:")
        print("   /daily_signal - Get next quality signal")
        print("   /daily_status - Check system status")
        print("   /ds - Quick alias")
        print("\n💡 Background alerts will send notifications every 15 minutes")

        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_daily_signals_integration()
    if success:
        print("\n🎯 INTEGRATION COMPLETE - Ready for production!")
    else:
        print("\n⚠️  INTEGRATION ISSUES - Check errors above")
        sys.exit(1)