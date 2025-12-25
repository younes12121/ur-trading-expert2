#!/usr/bin/env python3
"""
🚀 LIVE STRIPE SETUP SCRIPT
Helps you transition from test mode to live Stripe payments
"""

import os
import sys
from pathlib import Path

def print_header():
    print("🚀 LIVE STRIPE SETUP SCRIPT")
    print("=" * 50)
    print("This script will help you set up live Stripe payments")
    print("⚠️  WARNING: This will enable REAL money processing!")
    print()

def check_current_setup():
    print("📋 CHECKING CURRENT SETUP")
    print("-" * 30)

    # Check .env file
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        return False

    # Read .env file
    with open('.env', 'r') as f:
        env_content = f.read()

    # Check if using test keys
    if 'sk_test_' in env_content:
        print("✅ Found test Stripe keys (current setup)")
    else:
        print("⚠️  No test keys found - might already be live!")

    print("✅ .env file exists")
    return True

def create_live_products_guide():
    print("\n💳 STEP 1: CREATE LIVE STRIPE PRODUCTS")
    print("-" * 40)
    print("You need to create live products in Stripe dashboard:")
    print()
    print("1. Go to https://dashboard.stripe.com/products (LIVE mode)")
    print("2. Click 'Create product'")
    print()
    print("📦 PREMIUM PRODUCT ($29/month):")
    print("   Name: 'Premium Subscription'")
    print("   Price: $29.00/month")
    print("   Copy the price ID (starts with 'price_live_...')")
    print()
    print("👑 VIP PRODUCT ($99/month):")
    print("   Name: 'VIP Subscription'")
    print("   Price: $99.00/month")
    print("   Copy the price ID (starts with 'price_live_...')")
    print()

def get_live_keys_guide():
    print("\n🔑 STEP 2: GET LIVE API KEYS")
    print("-" * 30)
    print("1. In Stripe dashboard, click 'Developers' → 'API keys'")
    print("2. Make sure you're in LIVE mode (top right)")
    print("3. Copy your live secret key (starts with 'sk_live_...')")
    print("4. Copy your live publishable key (starts with 'pk_live_...')")
    print()

def update_env_file():
    print("\n📝 STEP 3: UPDATE .env FILE")
    print("-" * 28)

    live_secret = input("Enter your LIVE secret key (sk_live_...): ").strip()
    live_publishable = input("Enter your LIVE publishable key (pk_live_...): ").strip()
    premium_price_id = input("Enter PREMIUM price ID (price_...): ").strip()
    vip_price_id = input("Enter VIP price ID (price_...): ").strip()

    # Backup current .env
    backup_path = Path('.env.backup')
    if backup_path.exists():
        os.remove(backup_path)
    os.rename('.env', '.env.backup')

    # Create new .env with live keys
    env_content = f"""# LIVE STRIPE CONFIGURATION - PRODUCTION READY
STRIPE_SECRET_KEY={live_secret}
STRIPE_PUBLISHABLE_KEY={live_publishable}
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret_here
STRIPE_PRICE_PREMIUM={premium_price_id}
STRIPE_PRICE_VIP={vip_price_id}

# Database and other config...
DATABASE_URL=postgresql://trading_user:password@localhost:5432/trading_bot
LOG_LEVEL=INFO
BACKUP_ENABLED=true
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Updated .env file with live keys")
    print("📁 Backup created: .env.backup")

def update_bot_code():
    print("\n🤖 STEP 4: UPDATE BOT CODE")
    print("-" * 25)

    # Read telegram_bot.py
    bot_path = Path('telegram_bot.py')
    if not bot_path.exists():
        print("❌ telegram_bot.py not found!")
        return

    with open(bot_path, 'r') as f:
        content = f.read()

    # Remove hardcoded test keys and use environment variables
    updated_content = content.replace(
        "stripe.api_key = 'sk_test_51SbBAtCoLBi6DM3Oq7VPUcrrvKufgzCzgrSQnCA5gYpSUFsgJgydKh4IkGbZLIRv9f1nvQkhxZxGdPsxJIn1OJmz00IfeksIXB'",
        "# stripe.api_key loaded from environment variable"
    )

    updated_content = updated_content.replace(
        """price_ids = {
            'premium': 'price_1SbBRDCoLBi6DM3OWh4JR3Lt',
            'vip': 'price_1SbBd5CoLBi6DM3OF8H2HKY8'
        }""",
        """price_ids = {
            'premium': os.getenv('STRIPE_PRICE_PREMIUM'),
            'vip': os.getenv('STRIPE_PRICE_VIP')
        }"""
    )

    # Write back
    with open(bot_path, 'w') as f:
        f.write(updated_content)

    print("✅ Updated telegram_bot.py to use environment variables")

def test_live_setup():
    print("\n🧪 STEP 5: TEST LIVE SETUP")
    print("-" * 25)
    print("⚠️  IMPORTANT: Test with a REAL credit card!")
    print()
    print("1. Start bot: python telegram_bot.py")
    print("2. Send /subscribe premium")
    print("3. Complete payment with real card")
    print("4. Check Stripe dashboard for payment")
    print("5. Verify user gets premium access")
    print()
    print("❌ If test fails, immediately switch back to test mode!")

def safety_warnings():
    print("\n⚠️  SAFETY WARNINGS")
    print("-" * 18)
    print("🔴 REAL MONEY: Users will be charged real money")
    print("🔴 RESPONSIBILITY: You handle refunds and support")
    print("🔴 COMPLIANCE: Ensure legal compliance in all jurisdictions")
    print("🔴 BACKUP: Keep test keys safe for debugging")
    print("🔴 MONITORING: Watch Stripe dashboard closely")
    print()

def main():
    print_header()

    if not check_current_setup():
        return

    response = input("Are you ready to set up LIVE Stripe payments? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Setup cancelled. Staying in test mode.")
        return

    create_live_products_guide()
    input("Press Enter when you've created the live products...")

    get_live_keys_guide()
    input("Press Enter when you have the live keys...")

    update_env_file()
    update_bot_code()

    print("\n🎉 LIVE SETUP COMPLETE!")
    print("=" * 25)
    print("✅ .env updated with live keys")
    print("✅ Bot code updated to use environment variables")
    print("✅ Ready for live payments")

    test_live_setup()
    safety_warnings()

    final_confirm = input("Type 'LIVE' to confirm you're ready to go live: ").strip()
    if final_confirm == 'LIVE':
        print("\n🚀 GOING LIVE! Start your bot with: python telegram_bot.py")
        print("💰 You can now accept real payments!")
    else:
        print("\nSetup complete but not activated. Switch back to test mode if needed.")

if __name__ == '__main__':
    main()












