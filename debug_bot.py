#!/usr/bin/env python3
"""
Debug bot startup issues
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_bot_startup():
    print("🔍 Debugging bot startup issues...")
    print("=" * 50)

    try:
        # Test basic imports
        print("1. Testing basic imports...")
        from telegram_bot import check_network_connectivity, BOT_TOKEN
        print("✅ Basic imports successful")

        # Test network connectivity
        print("\n2. Testing network connectivity...")
        network_ok = check_network_connectivity()
        if network_ok:
            print("✅ Network connectivity: OK")
        else:
            print("⚠️ Network connectivity: FAILED (continuing anyway)")

        # Test BOT_TOKEN
        print("\n3. Testing BOT_TOKEN...")
        if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
            print("✅ BOT_TOKEN is set")
            print(f"   Token starts with: {BOT_TOKEN[:20]}...")
        else:
            print("❌ BOT_TOKEN is not set properly")
            return False

        # Test Telegram connection (basic)
        print("\n4. Testing Telegram connection...")
        try:
            from telegram import Bot
            bot = Bot(token=BOT_TOKEN)
            print("✅ Telegram bot object created")
        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            return False

        print("\n✅ All basic tests passed!")
        print("The bot should start successfully.")
        print("If it still crashes, there might be an issue with:")
        print("- Command handlers (check for syntax errors)")
        print("- Database connections")
        print("- Missing dependencies")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Check if all required packages are installed:")
        print("pip install python-telegram-bot stripe python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bot_startup()
    exit(0 if success else 1)
