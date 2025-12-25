#!/usr/bin/env python3
"""
Simple test script to verify the bot responds to /start command
"""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Check if bot token is set
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set!")
    print("Please set it in your .env file or environment variables")
    sys.exit(1)

print(f"SUCCESS: Bot token found: {BOT_TOKEN[:10]}...")

# Try to import and start the bot
try:
    print("\nINFO: Importing telegram_bot module...")
    import telegram_bot

    print("SUCCESS: Module imported successfully")
    print("\nSTARTING: Starting bot...")
    print("=" * 60)
    print("Bot should now be running. Try sending /start in Telegram.")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    
    # Start the bot
    telegram_bot.main()
    
except KeyboardInterrupt:
    print("\n\nSTOPPED: Bot stopped by user")
except Exception as e:
    print(f"\nERROR: Error starting bot: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
