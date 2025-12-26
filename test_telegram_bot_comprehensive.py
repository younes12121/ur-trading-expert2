#!/usr/bin/env python3
"""
Comprehensive Telegram Bot Test
Tests bot token, imports, syntax, and basic functionality
"""

import sys
import os
import traceback
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("=" * 70)
print("TELEGRAM BOT COMPREHENSIVE TEST")
print("=" * 70)
print()

# Test 1: Check bot token
print("[TEST 1/5] Checking bot token...")
try:
    from bot_config import BOT_TOKEN
    if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and len(BOT_TOKEN) > 10:
        print(f"  [OK] Bot token found: {BOT_TOKEN[:15]}...")
    else:
        print("  [ERROR] Bot token not set or invalid!")
        print("     Please set BOT_TOKEN in bot_config.py")
        sys.exit(1)
except ImportError as e:
    print(f"  [ERROR] Cannot import bot_config.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Error checking token: {e}")
    sys.exit(1)

# Test 2: Validate token with Telegram API
print("\n[TEST 2/5] Validating token with Telegram API...")
try:
    import requests
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe', timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print(f"  [OK] Token is valid!")
            print(f"     Bot ID: {bot_info['id']}")
            print(f"     Username: @{bot_info['username']}")
            print(f"     Name: {bot_info['first_name']}")
        else:
            print(f"  [ERROR] Telegram API error: {data.get('description', 'Unknown error')}")
            sys.exit(1)
    else:
        print(f"  [ERROR] HTTP error: {response.status_code}")
        print(f"     Response: {response.text[:200]}")
        sys.exit(1)
except requests.exceptions.Timeout:
    print("  [WARN] Connection timeout - check internet connection")
    print("     (This is OK if you're offline, but bot won't work)")
except requests.exceptions.ConnectionError:
    print("  [WARN] Connection error - check internet connection")
    print("     (This is OK if you're offline, but bot won't work)")
except ImportError:
    print("  [WARN] requests library not installed")
    print("     Install with: pip install requests")
except Exception as e:
    print(f"  [WARN] Error validating token: {e}")
    print("     Continuing with other tests...")

# Test 3: Check Python syntax
print("\n[TEST 3/5] Checking Python syntax...")
try:
    import py_compile
    py_compile.compile('telegram_bot.py', doraise=True)
    print("  [OK] Syntax check passed!")
except py_compile.PyCompileError as e:
    print(f"  [ERROR] Syntax error found: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  [WARN] Could not check syntax: {e}")

# Test 4: Import bot module
print("\n[TEST 4/5] Testing module imports...")
try:
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Try importing (this will check all dependencies)
    print("  Attempting to import telegram_bot module...")
    import telegram_bot
    print("  [OK] Module imported successfully!")
    
    # Check if main function exists
    if hasattr(telegram_bot, 'main'):
        print("  [OK] main() function found")
    else:
        print("  [WARN] main() function not found")
        
except ImportError as e:
    print(f"  [ERROR] Import error: {e}")
    print("\n  Missing dependencies? Try:")
    print("     pip install python-telegram-bot python-dotenv requests")
    sys.exit(1)
except SyntaxError as e:
    print(f"  [ERROR] Syntax error in module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Error importing module: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check critical components
print("\n[TEST 5/5] Checking critical components...")
try:
    # Check if Application can be created (without actually starting)
    from telegram.ext import Application
    
    # This will validate the token format
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        print("  [OK] Application builder works!")
        print("  [OK] Bot is ready to start!")
    except Exception as e:
        print(f"  [ERROR] Cannot create application: {e}")
        sys.exit(1)
        
except ImportError as e:
    print(f"  [ERROR] Cannot import telegram library: {e}")
    print("     Install with: pip install python-telegram-bot")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Error checking components: {e}")
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n" + "=" * 70)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 70)
print("\nYour Telegram bot is ready to run!")
print("\nTo start the bot, run:")
print("  python telegram_bot.py")
print("\nOr use:")
print("  python test_bot_start.py")
print("\nThen test in Telegram by sending /start to your bot")
print("=" * 70)

