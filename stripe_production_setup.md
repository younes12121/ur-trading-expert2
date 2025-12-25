# Stripe Production Setup Guide

## Overview
This guide will help you migrate from Stripe test mode to production mode for your UR Trading Expert bot.

## Current Status
- **Mode:** Test mode
- **API Key:** Hardcoded test key in `telegram_bot.py`
- **Price IDs:** Test price IDs

## Step 1: Create Stripe Business Account

1. Go to: https://dashboard.stripe.com/register
2. Click "Create account"
3. Choose "Business" account type
4. Fill in business information:
   - Business name: UR Trading Expert LLC
   - Business type: LLC
   - Industry: Financial Services / Trading
   - Website: https://urtradingexpert.com
   - Business address: Your Wyoming LLC address
   - EIN: (You'll need this from IRS application)

## Step 2: Complete Business Verification

Stripe will require:
- **Business Information:**
  - Legal business name
  - EIN (Employer Identification Number)
  - Business address
  - Business phone number
  
- **Business Owner Information:**
  - Full legal name
  - Date of birth
  - Home address
  - SSN (last 4 digits)
  - Government-issued ID

- **Bank Account:**
  - Business bank account details
  - Routing number
  - Account number

**Timeline:** Verification typically takes 1-2 business days, but can take up to 2 weeks.

## Step 3: Create Production Products and Prices

Once verified, create your subscription products:

### Premium Subscription ($39/month)
1. Go to Products → Add Product
2. Name: "Premium Subscription"
3. Description: "Full access to all trading signals and AI features"
4. Pricing:
   - Price: $39.00
   - Billing period: Monthly
   - Recurring: Yes
5. Save and note the **Price ID** (starts with `price_`)

### VIP Subscription ($129/month)
1. Go to Products → Add Product
2. Name: "VIP Subscription"
3. Description: "All Premium features plus broker integration"
4. Pricing:
   - Price: $129.00
   - Billing period: Monthly
   - Recurring: Yes
5. Save and note the **Price ID** (starts with `price_`)

## Step 4: Get Production API Keys

1. Go to: Developers → API keys
2. Make sure you're in **Live mode** (toggle in top right)
3. Copy:
   - **Publishable key** (starts with `pk_live_`)
   - **Secret key** (starts with `sk_live_`) - Click "Reveal" to see it

**IMPORTANT:** Never commit secret keys to version control!

## Step 5: Update Bot Code

### Option A: Environment Variables (Recommended)

1. Create `.env` file (if not exists):
```bash
STRIPE_SECRET_KEY=sk_live_YOUR_PRODUCTION_SECRET_KEY
STRIPE_PREMIUM_PRICE_ID=price_YOUR_PREMIUM_PRICE_ID
STRIPE_VIP_PRICE_ID=price_YOUR_VIP_PRICE_ID
```

2. Update `telegram_bot.py` subscribe_command:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# In subscribe_command function:
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')  # Fallback to test

price_ids = {
    'premium': os.getenv('STRIPE_PREMIUM_PRICE_ID', 'price_test_...'),
    'vip': os.getenv('STRIPE_VIP_PRICE_ID', 'price_test_...')
}
```

### Option B: Configuration File

1. Create `stripe_config.py`:
```python
# Production Stripe Configuration
STRIPE_SECRET_KEY = 'sk_live_YOUR_PRODUCTION_SECRET_KEY'
STRIPE_PREMIUM_PRICE_ID = 'price_YOUR_PREMIUM_PRICE_ID'
STRIPE_VIP_PRICE_ID = 'price_YOUR_VIP_PRICE_ID'
```

2. Update `telegram_bot.py`:
```python
from stripe_config import STRIPE_SECRET_KEY, STRIPE_PREMIUM_PRICE_ID, STRIPE_VIP_PRICE_ID

# In subscribe_command:
stripe.api_key = STRIPE_SECRET_KEY
price_ids = {
    'premium': STRIPE_PREMIUM_PRICE_ID,
    'vip': STRIPE_VIP_PRICE_ID
}
```

## Step 6: Set Up Webhooks

Webhooks allow Stripe to notify your bot about payment events.

1. Go to: Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-domain.com/stripe-webhook`
   - You'll need to set up a webhook endpoint in your bot
4. Select events to listen to:
   - `checkout.session.completed` - When payment succeeds
   - `customer.subscription.created` - When subscription starts
   - `customer.subscription.updated` - When subscription changes
   - `customer.subscription.deleted` - When subscription cancels
   - `invoice.payment_succeeded` - When monthly payment succeeds
   - `invoice.payment_failed` - When payment fails
5. Copy the **Webhook signing secret** (starts with `whsec_`)

## Step 7: Test Production Payments

**IMPORTANT:** Test with real cards in small amounts first!

1. Use a real credit card with a small amount
2. Test successful payment flow
3. Test subscription cancellation
4. Verify webhook events are received
5. Check that user tier is updated correctly

## Step 8: Update Success/Cancel URLs

Update the URLs in your checkout session creation:

```python
success_url=f"https://t.me/{context.bot.username}?start=payment_success_{tier}",
cancel_url=f"https://t.me/{context.bot.username}?start=payment_cancelled"
```

## Step 9: Handle Webhook Events

Create a webhook handler to process Stripe events:

```python
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Update user tier in database
        user_id = session['metadata']['telegram_id']
        tier = session['metadata']['tier']
        user_manager.update_user_tier(user_id, tier)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Downgrade user to free tier
        # ...
    
    return jsonify({'status': 'success'}), 200
```

## Step 10: Security Best Practices

1. **Never commit API keys to Git:**
   - Add `.env` to `.gitignore`
   - Add `stripe_config.py` to `.gitignore` if it contains keys

2. **Use environment variables** for all sensitive data

3. **Rotate keys regularly** if compromised

4. **Monitor Stripe Dashboard** for suspicious activity

5. **Set up email alerts** in Stripe for:
   - Failed payments
   - Disputes/chargebacks
   - Security events

## Step 11: Payment Disputes and Refunds

### Handling Disputes
- Stripe will notify you of disputes
- Respond within 7 days
- Provide evidence (screenshots, terms of service)
- Most disputes can be won with proper documentation

### Refund Policy
- Implement your refund policy (7-day money-back guarantee)
- Process refunds through Stripe Dashboard or API
- Update user tier when refunding

## Step 12: Go Live Checklist

- [ ] Stripe business account created
- [ ] Business verification completed
- [ ] Production products and prices created
- [ ] Production API keys obtained
- [ ] Bot code updated with production keys
- [ ] Webhooks configured and tested
- [ ] Test payments completed successfully
- [ ] Success/cancel URLs updated
- [ ] Webhook handler implemented
- [ ] Security measures in place
- [ ] Monitoring and alerts set up
- [ ] Refund policy implemented

## Support Resources

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Support:** https://support.stripe.com
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Stripe API Reference:** https://stripe.com/docs/api

## Common Issues

### Issue: Verification Taking Too Long
**Solution:** Contact Stripe support, ensure all documents are clear and complete

### Issue: Webhooks Not Working
**Solution:** 
- Check webhook URL is accessible
- Verify webhook secret is correct
- Test with Stripe CLI: `stripe listen --forward-to localhost:5000/stripe-webhook`

### Issue: Payments Not Processing
**Solution:**
- Verify API keys are production keys (not test)
- Check account is fully verified
- Ensure bank account is connected

## Next Steps After Production Setup

1. Monitor first few transactions closely
2. Set up automated email notifications
3. Create customer support workflow for payment issues
4. Implement subscription management commands
5. Add payment history tracking
6. Set up analytics for subscription metrics

---

**Remember:** Always test thoroughly in test mode before going live, and start with small real transactions to verify everything works correctly.
