#!/usr/bin/env python3
"""
Test bot token validity
"""
import requests
from bot_config import BOT_TOKEN

def test_bot_token():
    try:
        print(f"Testing bot token: {BOT_TOKEN[:20]}...")
        response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe', timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print("✅ Bot token is valid!")
                print(f"   Bot ID: {bot_info['id']}")
                print(f"   Username: @{bot_info['username']}")
                print(f"   Name: {bot_info['first_name']}")
                return True
            else:
                print(f"❌ Telegram API error: {data}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Connection timeout - check internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet connection")
        return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

if __name__ == "__main__":
    success = test_bot_token()
    exit(0 if success else 1)
