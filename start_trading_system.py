#!/usr/bin/env python3
"""
Trading System Startup Script
Starts both the Telegram bot and the dashboard API
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

def start_dashboard_api():
    """Start the personal dashboard API server"""
    print("🚀 Starting Personal Dashboard API...")
    try:
        # Import and run the dashboard API
        from personal_dashboard_api import app

        # Run on port 5001 to avoid conflicts
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,  # Disable debug in production
            threaded=True,
            use_reloader=False  # Disable reloader to avoid conflicts
        )
    except Exception as e:
        print(f"❌ Failed to start dashboard API: {e}")
        return False
    return True

def start_telegram_bot():
    """Start the Telegram bot"""
    print("🤖 Starting Telegram Trading Bot...")
    try:
        # Import the bot module
        import telegram_bot
        # Call main() to start the bot (this will block)
        print("✅ Telegram bot module loaded, starting bot...")
        telegram_bot.main()
        return True
    except KeyboardInterrupt:
        print("\n🛑 Telegram bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start Telegram bot: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    print("🎯 STARTING COMPLETE TRADING SYSTEM")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check environment variables
    required_env_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set these in your .env file or environment")
        print()

    # Start dashboard API in a separate thread
    dashboard_thread = threading.Thread(target=start_dashboard_api, daemon=True)
    dashboard_thread.start()

    # Give dashboard a moment to start
    time.sleep(2)

    # Start the Telegram bot (this will block)
    try:
        bot_success = start_telegram_bot()
        if bot_success:
            print("\n🎉 Trading system started successfully!")
            print("\n📋 System Components:")
            print("   • Telegram Bot: Running")
            print("   • Dashboard API: http://localhost:5001")
            print("   • Database: SQLite (trading_expert.db)")
            print("\n📱 Telegram Commands:")
            print("   • /start - Get started")
            print("   • /dashboard - View your personal dashboard")
            print("   • /portfolio - Detailed portfolio analysis")
            print("   • /execute - Execute AI-enhanced trades")
            print("   • /performance - Trading performance analytics")
            print("   • /help - Full command list")
            print("\n🌐 Dashboard URLs:")
            print("   • System Dashboard: http://localhost:5001")
            print("   • User Dashboard: http://localhost:5001/dashboard/<telegram_id>")
            print("\nPress Ctrl+C to stop the system")
            print("=" * 50)

            # Keep the main thread alive
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down trading system...")
        print("✅ System stopped successfully")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())







