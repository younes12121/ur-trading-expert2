#!/usr/bin/env python3
"""
Simple bot status checker - no Unicode issues
"""

import sys
import os
import io

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("=" * 60)
print("TELEGRAM BOT STATUS CHECK")
print("=" * 60)
print()

# Check 1: Bot Token
print("[1] Checking bot token...")
try:
    from bot_config import BOT_TOKEN
    if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and len(BOT_TOKEN) > 10:
        print(f"    OK - Token found: {BOT_TOKEN[:20]}...")
    else:
        print("    ERROR - Token not set!")
        sys.exit(1)
except Exception as e:
    print(f"    ERROR - {e}")
    sys.exit(1)

# Check 2: Validate with Telegram
print("\n[2] Validating token with Telegram API...")
try:
    import requests
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print(f"    OK - Bot is valid!")
            print(f"    Bot ID: {bot_info['id']}")
            print(f"    Username: @{bot_info['username']}")
            print(f"    Name: {bot_info['first_name']}")
        else:
            print(f"    ERROR - API returned: {data.get('description')}")
            sys.exit(1)
    else:
        print(f"    ERROR - HTTP {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"    WARNING - Could not validate: {e}")
    print("    (This is OK if offline)")

# Check 3: Syntax
print("\n[3] Checking syntax...")
try:
    import py_compile
    py_compile.compile('telegram_bot.py', doraise=True)
    print("    OK - No syntax errors")
except Exception as e:
    print(f"    ERROR - Syntax error: {e}")
    sys.exit(1)

# Check 4: Can import
print("\n[4] Testing imports...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print("    Attempting to import telegram_bot...")
    import telegram_bot
    print("    OK - Module imported successfully")
    
    # Check main function
    if hasattr(telegram_bot, 'main'):
        print("    OK - main() function exists")
    else:
        print("    WARNING - main() function not found")
        
except ImportError as e:
    print(f"    ERROR - Import failed: {e}")
    print("    Try: pip install python-telegram-bot python-dotenv requests")
    sys.exit(1)
except Exception as e:
    print(f"    ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 5: Application builder
print("\n[5] Testing application builder...")
try:
    from telegram.ext import Application
    app = Application.builder().token(BOT_TOKEN).build()
    print("    OK - Application can be created")
    print("    OK - Bot is ready to run!")
except Exception as e:
    print(f"    ERROR - Cannot create application: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("RESULT: Bot is WORKING and ready to use!")
print("=" * 60)
print("\nTo start the bot, run:")
print("  python telegram_bot.py")
print("\nThen test in Telegram by sending /start to your bot")
print("=" * 60)


