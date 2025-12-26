# Stripe Code Migration Guide

## Current Status
The `subscribe_command` in `telegram_bot.py` currently uses hardcoded test Stripe keys. This guide shows how to migrate to production-ready code using environment variables.

## Location
File: `telegram_bot.py`  
Function: `subscribe_command` (around line 8160)

## Current Code (Test Mode)
```python
# HARDCODED - Direct Stripe integration
try:
    import stripe
    
    # HARDCODED SECRET KEY - Direct from Stripe
    stripe.api_key = 'sk_test_YOUR_STRIPE_SECRET_KEY_HERE'
    
    # HARDCODED Price IDs
    price_ids = {
        'premium': 'price_1SbBRDCoLBi6DM3OWh4JR3Lt',
        'vip': 'price_1SbBd5CoLBi6DM3OF8H2HKY8'
    }
```

## Production-Ready Code

### Step 1: Ensure dotenv is loaded
At the top of `telegram_bot.py`, make sure you have:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 2: Update subscribe_command function
Replace the hardcoded Stripe section with:

```python
# Production Stripe integration with environment variables
try:
    import stripe
    import os
    
    # Get Stripe keys from environment variables
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe_secret_key:
        # Fallback to test key if not set (for development)
        stripe_secret_key = os.getenv('STRIPE_TEST_SECRET_KEY', 'sk_test_...')
        await update.message.reply_text(
            "⚠️ Payment system is in test mode. Contact support for production access."
        )
    
    stripe.api_key = stripe_secret_key
    
    # Get Price IDs from environment variables
    price_ids = {
        'premium': os.getenv('STRIPE_PREMIUM_PRICE_ID', 'price_test_...'),
        'vip': os.getenv('STRIPE_VIP_PRICE_ID', 'price_test_...')
    }
    
    # Validate that we have production keys
    if stripe_secret_key.startswith('sk_test_'):
        # Still in test mode - warn user
        test_mode_warning = "\n\n⚠️ Currently in TEST MODE - Use test card: 4242 4242 4242 4242"
    else:
        test_mode_warning = ""
    
    # Create checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_ids[tier],
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f"https://t.me/{context.bot.username}?start=payment_success_{tier}",
        cancel_url=f"https://t.me/{context.bot.username}?start=payment_cancelled",
        metadata={
            'telegram_id': user_id,
            'tier': tier,
            'bot_username': context.bot.username
        },
        customer_email=None,  # Optional: collect email during checkout
        allow_promotion_codes=True  # Allow discount codes
    )
    
    # Success - send link
    price = 39 if tier == 'premium' else 129  # Updated to actual prices
    msg = f"💳 **{tier.upper()} SUBSCRIPTION**\n\n"
    msg += f"Price: **${price}/month**\n\n"
    msg += "Click the link below to complete payment:\n"
    msg += f"{session.url}{test_mode_warning}\n\n"
    msg += "✅ Secure payment via Stripe\n"
    msg += "🔄 Auto-renewal monthly\n"
    msg += "❌ Cancel anytime"
    
    await update.message.reply_text(msg, parse_mode='Markdown')
    
except ImportError:
    await update.message.reply_text(
        "❌ Payment system unavailable. Please install stripe: pip install stripe"
    )
except stripe.error.StripeError as e:
    await update.message.reply_text(
        f"❌ Payment error: {str(e)}\n\nPlease contact support@urtradingexpert.com"
    )
except Exception as e:
    await update.message.reply_text(
        f"❌ Unexpected error: {str(e)}\n\nPlease contact support@urtradingexpert.com"
    )
```

## Environment Variables Setup

### Create .env file
Create a `.env` file in your project root (see `.env.example` for template):

```bash
# Stripe Production Keys
STRIPE_SECRET_KEY=sk_live_your_production_secret_key_here
STRIPE_PREMIUM_PRICE_ID=price_your_premium_price_id_here
STRIPE_VIP_PRICE_ID=price_your_vip_price_id_here

# Optional: Keep test keys for development
STRIPE_TEST_SECRET_KEY=sk_test_YOUR_STRIPE_SECRET_KEY_HERE
```

### Security Notes
1. **NEVER commit .env to Git** - Already in `.gitignore`
2. **Use different keys for development and production**
3. **Rotate keys if compromised**
4. **Store production keys securely** (use secrets management in production)

## Testing the Migration

### Test Mode (Development)
1. Keep test keys in `.env`
2. Code will automatically use test keys
3. Test with card: 4242 4242 4242 4242

### Production Mode
1. Replace with production keys in `.env`
2. Verify keys start with `sk_live_` and `pk_live_`
3. Test with small real transaction first
4. Monitor Stripe dashboard for activity

## Migration Checklist

- [ ] Create `.env` file from `.env.example`
- [ ] Add production Stripe keys to `.env`
- [ ] Update `subscribe_command` function with new code
- [ ] Test in test mode first
- [ ] Verify environment variables are loaded
- [ ] Test payment flow end-to-end
- [ ] Switch to production keys
- [ ] Test with small real transaction
- [ ] Monitor Stripe dashboard
- [ ] Update success/cancel URL handlers

## Rollback Plan

If something goes wrong:
1. Revert to hardcoded test keys temporarily
2. Check environment variable loading
3. Verify `.env` file is in correct location
4. Check file permissions on `.env`
5. Verify `python-dotenv` is installed: `pip install python-dotenv`

## Additional Improvements

### Webhook Integration
After migration, implement webhook handler for:
- Subscription created
- Subscription updated
- Subscription cancelled
- Payment succeeded
- Payment failed

See `stripe_production_setup.md` for webhook implementation details.

### Error Handling
Add comprehensive error handling for:
- Network errors
- Stripe API errors
- Invalid price IDs
- Missing environment variables
- Rate limiting

### Logging
Add logging for:
- Payment attempts
- Successful payments
- Failed payments
- Subscription changes

---

**Important:** Always test thoroughly in test mode before switching to production keys!
