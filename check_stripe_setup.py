"""
Quick Stripe Setup Checker
Run this to verify your Stripe configuration is correct
"""

import os
import sys

def check_setup():
    """Check if Stripe setup is complete"""
    print("=" * 60)
    print("🔍 STRIPE SETUP CHECKER")
    print("=" * 60)
    print()
    
    checks_passed = 0
    total_checks = 8
    
    # Check 1: .env file exists
    print("📄 Checking .env file...")
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("   ✅ .env file exists")
        checks_passed += 1
    else:
        print("   ❌ .env file NOT found")
        print("      Create .env file in backtesting folder")
    print()
    
    # Check 2: Load environment variables
    print("🔑 Checking environment variables...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("   ✅ python-dotenv installed")
        checks_passed += 1
    except ImportError:
        print("   ❌ python-dotenv NOT installed")
        print("      Run: pip install python-dotenv")
        return
    print()
    
    # Check 3: Stripe library
    print("📦 Checking Stripe library...")
    try:
        import stripe
        print(f"   ✅ Stripe installed (version {stripe.__version__})")
        checks_passed += 1
    except ImportError:
        print("   ❌ Stripe NOT installed")
        print("      Run: pip install stripe")
        return
    print()
    
    # Check 4: Secret Key
    print("🔐 Checking STRIPE_SECRET_KEY...")
    secret_key = os.getenv('STRIPE_SECRET_KEY')
    if secret_key and secret_key.startswith('sk_test_'):
        print(f"   ✅ Secret key found: {secret_key[:20]}...")
        checks_passed += 1
    elif secret_key and secret_key.startswith('sk_live_'):
        print(f"   ⚠️  LIVE secret key found (use test key for testing)")
        print(f"      {secret_key[:20]}...")
        checks_passed += 1
    else:
        print("   ❌ Secret key NOT found or invalid")
        print("      Should start with 'sk_test_' or 'sk_live_'")
    print()
    
    # Check 5: Publishable Key
    print("🔓 Checking STRIPE_PUBLISHABLE_KEY...")
    pub_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    if pub_key and pub_key.startswith('pk_test_'):
        print(f"   ✅ Publishable key found: {pub_key[:20]}...")
        checks_passed += 1
    elif pub_key and pub_key.startswith('pk_live_'):
        print(f"   ⚠️  LIVE publishable key found (use test key for testing)")
        print(f"      {pub_key[:20]}...")
        checks_passed += 1
    else:
        print("   ❌ Publishable key NOT found or invalid")
        print("      Should start with 'pk_test_' or 'pk_live_'")
    print()
    
    # Check 6: Webhook Secret
    print("🔔 Checking STRIPE_WEBHOOK_SECRET...")
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if webhook_secret and webhook_secret.startswith('whsec_'):
        print(f"   ✅ Webhook secret found: {webhook_secret[:15]}...")
        checks_passed += 1
    else:
        print("   ⚠️  Webhook secret NOT found or invalid")
        print("      Should start with 'whsec_'")
        print("      (This is optional until you deploy)")
    print()
    
    # Check 7: Premium Price ID
    print("💰 Checking STRIPE_PRICE_PREMIUM...")
    premium_price = os.getenv('STRIPE_PRICE_PREMIUM')
    expected_premium = 'price_1SbBRDCoLBi6DM3OWh4JR3Lt'
    if premium_price == expected_premium:
        print(f"   ✅ Premium price ID correct: {premium_price}")
        checks_passed += 1
    else:
        print(f"   ❌ Premium price ID incorrect or missing")
        print(f"      Expected: {expected_premium}")
        print(f"      Got: {premium_price}")
    print()
    
    # Check 8: VIP Price ID
    print("💎 Checking STRIPE_PRICE_VIP...")
    vip_price = os.getenv('STRIPE_PRICE_VIP')
    expected_vip = 'price_1SbBd5CoLBi6DM3OF8H2HKY8'
    if vip_price == expected_vip:
        print(f"   ✅ VIP price ID correct: {vip_price}")
        checks_passed += 1
    else:
        print(f"   ❌ VIP price ID incorrect or missing")
        print(f"      Expected: {expected_vip}")
        print(f"      Got: {vip_price}")
    print()
    
    # Summary
    print("=" * 60)
    print(f"📊 RESULTS: {checks_passed}/{total_checks} checks passed")
    print("=" * 60)
    print()
    
    if checks_passed == total_checks:
        print("🎉 EXCELLENT! Your Stripe setup is COMPLETE! 🎉")
        print()
        print("✅ Next steps:")
        print("   1. Test payment handler: python payment_handler.py")
        print("   2. Start your bot: python telegram_bot.py")
        print("   3. Test /subscribe command in Telegram")
        print("   4. Use test card: 4242 4242 4242 4242")
        print()
    elif checks_passed >= 6:
        print("👍 GOOD! Almost there! Fix the remaining issues.")
        print()
        print("📝 TODO:")
        if checks_passed < 8:
            print("   - Verify all environment variables in .env file")
        if not webhook_secret or not webhook_secret.startswith('whsec_'):
            print("   - Add webhook secret (optional for testing)")
        print()
    else:
        print("⚠️  MORE SETUP NEEDED")
        print()
        print("📚 See these guides:")
        print("   - STRIPE_ACTION_PLAN.md (quick visual guide)")
        print("   - COMPLETE_STRIPE_NOW.md (5-minute guide)")
        print("   - STRIPE_SETUP_INSTRUCTIONS.md (detailed)")
        print()
    
    return checks_passed == total_checks

if __name__ == "__main__":
    try:
        success = check_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error running checker: {e}")
        sys.exit(1)



