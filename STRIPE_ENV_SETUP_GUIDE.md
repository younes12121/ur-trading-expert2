# Stripe Environment Variables Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create .env File

1. **Navigate to your project folder:**
   ```
   C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting
   ```

2. **Create a new file named `.env`** (with the dot at the start)
   - Windows: Right-click → New → Text Document
   - Name it: `.env` (Windows may warn you - that's OK)

3. **Open `.env` in a text editor** (Notepad, VS Code, etc.)

### Step 2: Get Your Stripe Keys

#### A. Get API Keys
1. Go to: https://dashboard.stripe.com/test/apikeys
2. **Publishable key** (already visible):
   - Copy the key starting with `pk_test_...`
3. **Secret key**:
   - Click "Reveal test key"
   - Copy the key starting with `sk_test_...`

#### B. Get Webhook Secret (Optional for now)
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "+ Add endpoint"
3. Enter URL: `https://example.com/stripe/webhook` (temporary - update later)
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
5. Click "Add endpoint"
6. Click on the new webhook
7. Click "Reveal" next to "Signing secret"
8. Copy the secret starting with `whsec_...`

### Step 3: Add Keys to .env File

Paste this into your `.env` file and replace the placeholder values:

```env
# Telegram Bot Token (already set in bot_config.py)
TELEGRAM_BOT_TOKEN=8437677554:AAHUZJf0R1gYHdsAvVEm3u5pOJq50CHXTiY

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Price IDs (already correct - don't change!)
STRIPE_PRICE_PREMIUM=price_1SbBRDCoLBi6DM3OWh4JR3Lt
STRIPE_PRICE_VIP=price_1SbBd5CoLBi6DM3OF8H2HKY8

# Admin User ID
ADMIN_USER_IDS=7713994326
```

**Replace:**
- `sk_test_YOUR_SECRET_KEY_HERE` → Your actual secret key from Step 2A
- `pk_test_YOUR_PUBLISHABLE_KEY_HERE` → Your actual publishable key from Step 2A
- `whsec_YOUR_WEBHOOK_SECRET_HERE` → Your actual webhook secret from Step 2B

### Step 4: Verify Setup

Run the setup checker:
```powershell
python check_stripe_setup.py
```

**Expected output:**
```
🔍 STRIPE SETUP CHECKER
========================
📄 Checking .env file...
   ✅ .env file exists
🔑 Checking environment variables...
   ✅ python-dotenv installed
📦 Checking Stripe library...
   ✅ Stripe installed
🔐 Checking STRIPE_SECRET_KEY...
   ✅ Secret key found: sk_test_...
🔓 Checking STRIPE_PUBLISHABLE_KEY...
   ✅ Publishable key found: pk_test_...
🔔 Checking STRIPE_WEBHOOK_SECRET...
   ✅ Webhook secret found: whsec_...
💰 Checking STRIPE_PRICE_PREMIUM...
   ✅ Premium price ID correct
💎 Checking STRIPE_PRICE_VIP...
   ✅ VIP price ID correct
========================
📊 RESULTS: 8/8 checks passed
🎉 EXCELLENT! Your Stripe setup is COMPLETE! 🎉
```

### Step 5: Test Payment Flow

1. **Start your bot:**
   ```powershell
   python telegram_bot.py
   ```

2. **In Telegram:**
   - Send: `/subscribe premium`
   - Click the payment link
   - Use test card: `4242 4242 4242 4242`
   - Expiry: `12/25`
   - CVC: `123`
   - ZIP: `12345`

3. **Verify:**
   - Payment processes successfully
   - Bot receives confirmation
   - User tier is upgraded

## Troubleshooting

### Error: ".env file not found"
- Make sure the file is named `.env` (with the dot)
- Make sure it's in the same folder as `telegram_bot.py`
- Windows may hide the file - enable "Show hidden files" in File Explorer

### Error: "STRIPE_SECRET_KEY not found"
- Check that you copied the entire key (starts with `sk_test_`)
- Make sure there are no extra spaces or quotes
- Verify the `.env` file is in the correct location

### Error: "python-dotenv not installed"
```powershell
pip install python-dotenv
```

### Error: "stripe not installed"
```powershell
pip install stripe
```

## Next Steps

After setup is complete:
1. ✅ Test payment flow with test card
2. ✅ Complete Stripe business application (can do without bank account)
3. ⏳ Wait for bank account approval
4. ⏳ Switch to live mode keys when ready
5. ⏳ Update webhook URL to production URL

## Security Notes

- ✅ **NEVER commit .env to Git** (already in .gitignore)
- ✅ **Keep secret keys private**
- ✅ **Use test keys for development**
- ✅ **Switch to live keys only after bank account is ready**

## Support

If you encounter issues:
- Check: `STRIPE_SETUP_INSTRUCTIONS.md`
- Check: `🚀_COMPLETE_STRIPE_SETUP.md`
- Run: `python check_stripe_setup.py`
- Contact: support@urtradingexpert.com

