# 🚀 Complete Stripe Setup NOW - 5 Minute Guide

**Your Progress:** 2/4 Steps Complete ✅

---

## ✅ Already Done

1. ✅ Premium Product: `price_1SbBRDCoLBi6DM3OWh4JR3Lt` ($29/month)
2. ✅ VIP Product: `price_1SbBd5CoLBi6DM3OF8H2HKY8` ($99/month)

---

## ⏳ Complete These 2 Steps

### Step 3: Set Up Webhook (2 minutes)

1. **Go to:** https://dashboard.stripe.com/test/webhooks
2. **Click:** "+ Add endpoint"
3. **Endpoint URL:** `https://example.com/stripe/webhook` (temporary, update later)
4. **Select events:**
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
5. **Click:** "Add endpoint"
6. **Copy:** Webhook signing secret (starts with `whsec_`)

### Step 4: Get API Keys (1 minute)

1. **Go to:** https://dashboard.stripe.com/test/apikeys
2. **Copy:**
   - Publishable key (`pk_test_...`)
   - Secret key (`sk_test_...`) - click "Reveal"

---

## 🔧 Configure Your Bot (2 minutes)

### Create `.env` File

1. **Location:** `C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\`
2. **Create file:** `.env`
3. **Paste this** (replace with YOUR actual keys):

```env
# Stripe Keys (replace with your actual keys from Step 4)
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Price IDs (already set - don't change)
STRIPE_PRICE_PREMIUM=price_1SbBRDCoLBi6DM3OWh4JR3Lt
STRIPE_PRICE_VIP=price_1SbBd5CoLBi6DM3OF8H2HKY8
```

### Install Required Packages

```bash
pip install stripe python-dotenv
```

---

## ✅ Test It

### Run Test

```bash
cd C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting
python payment_handler.py
```

**Expected:**
```
✅ Stripe configured successfully!
   Premium Price ID: price_1SbBRDCoLBi6DM3OWh4JR3Lt
   VIP Price ID: price_1SbBd5CoLBi6DM3OF8H2HKY8
   Webhook configured: Yes ✅
```

### Test Payment Flow

1. Start bot: `python telegram_bot.py`
2. Send `/subscribe` in Telegram
3. Test with card: `4242 4242 4242 4242`

---

## 📋 Quick Checklist

- [ ] Go to Stripe Webhooks
- [ ] Create webhook endpoint
- [ ] Copy webhook secret (`whsec_...`)
- [ ] Go to API Keys
- [ ] Copy publishable key (`pk_test_...`)
- [ ] Copy secret key (`sk_test_...`)
- [ ] Create `.env` file
- [ ] Paste all 3 keys into `.env`
- [ ] Run `pip install stripe python-dotenv`
- [ ] Test with `python payment_handler.py`
- [ ] Start bot and test `/subscribe`

---

## 🎉 When Done

Your bot will:
- ✅ Accept real payments (test mode)
- ✅ Automatically upgrade users
- ✅ Handle subscriptions
- ✅ Process webhooks

**Let's finish this! 💪**

---

## Need More Detail?

See: `STRIPE_SETUP_INSTRUCTIONS.md` for complete guide



