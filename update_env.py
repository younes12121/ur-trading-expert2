#!/usr/bin/env python3
"""
Script to update the .env file with the real Telegram bot token
Usage: python update_env.py YOUR_BOT_TOKEN
"""

import os
import sys

if len(sys.argv) != 2:
    print("Usage: python update_env.py YOUR_BOT_TOKEN")
    print("Example: python update_env.py 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    sys.exit(1)

new_token = sys.argv[1].strip()

# Read current .env file
env_path = '.env'
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the placeholder token
old_line = 'TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here'
new_line = f'TELEGRAM_BOT_TOKEN={new_token}'

if old_line in content:
    content = content.replace(old_line, new_line)

    # Write back to file
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: .env file updated successfully!")
    print(f"New token: {new_token[:15]}...")
    print("\nYou can now test the bot with: python test_bot_start.py")
else:
    print("❌ Could not find the placeholder token in .env file")
