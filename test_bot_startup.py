#!/usr/bin/env python3
"""Test script to debug bot startup issues"""
import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("TESTING BOT STARTUP")
print("="*60)
print()

try:
    print("[1] Importing telegram_bot module...")
    import telegram_bot
    print("    ✓ Module imported successfully")
    print(f"    Module __name__: {telegram_bot.__name__}")
    print()
    
    print("[2] Checking if main function exists...")
    if hasattr(telegram_bot, 'main'):
        print("    ✓ main() function exists")
        print(f"    main type: {type(telegram_bot.main)}")
    else:
        print("    ✗ main() function NOT FOUND!")
        sys.exit(1)
    print()
    
    print("[3] Testing if script is run directly...")
    if __name__ == "__main__":
        print("    ✓ This test script is run directly")
    else:
        print(f"    ✗ This script __name__ = {__name__}")
    print()
    
    print("[4] Attempting to call telegram_bot.main()...")
    try:
        telegram_bot.main()
        print("    ✓ main() returned (may have exited normally)")
    except SystemExit as e:
        print(f"    ! main() called sys.exit({e.code})")
    except Exception as e:
        print(f"    ✗ EXCEPTION in main(): {e}")
        traceback.print_exc()
    
except ImportError as e:
    print(f"    ✗ IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"    ✗ UNEXPECTED ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("="*60)
print("TEST COMPLETE")
print("="*60)
