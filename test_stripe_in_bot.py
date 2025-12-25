"""
Quick test to verify Stripe configuration in bot environment
"""

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

# Test payment handler
from payment_handler import PaymentHandler

payment_handler = PaymentHandler()

print("\n" + "="*50)
print("STRIPE CONFIGURATION TEST")
print("="*50)

print(f"\nStripe Available: {payment_handler.is_configured()}")

if payment_handler.is_configured():
    print("✅ Stripe is CONFIGURED and READY!")
    print(f"\nPremium Price ID: {payment_handler.price_ids.get('premium_monthly')}")
    print(f"VIP Price ID: {payment_handler.price_ids.get('vip_monthly')}")
    
    # Test checkout session generation
    print("\n" + "-"*50)
    print("Testing Checkout Session Generation...")
    print("-"*50)
    
    test_url = payment_handler.create_checkout_session(
        telegram_id=123456789,
        tier='premium',
        success_url='https://t.me/test?start=success',
        cancel_url='https://t.me/test?start=cancel'
    )
    
    if test_url:
        print("✅ Checkout URL generated successfully!")
        print(f"\nURL: {test_url[:80]}...")
        print("\n🎉 STRIPE PAYMENT SYSTEM IS FULLY FUNCTIONAL!")
    else:
        print("❌ Failed to generate checkout URL")
        print("Check your Stripe API keys")
else:
    print("❌ Stripe is NOT configured")
    print("\nPlease check:")
    print("1. .env file exists")
    print("2. STRIPE_SECRET_KEY is set")
    print("3. Keys are correct")

print("\n" + "="*50)

