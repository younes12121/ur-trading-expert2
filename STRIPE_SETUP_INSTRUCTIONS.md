# 🎯 Complete Your Stripe Setup - Step by Step

**Status:** Steps 1-2 Complete ✅ | Steps 3-4 In Progress ⏳

---

## ✅ What You've Already Done

- ✅ Step 1: Created Premium Product ($29/month)
  - Price ID: `price_1SbBRDCoLBi6DM3OWh4JR3Lt`
  
- ✅ Step 2: Created VIP Product ($99/month)
  - Price ID: `price_1SbBd5CoLBi6DM3OF8H2HKY8`

---

## ⏳ Step 3: Set Up Webhooks (15 minutes)

Webhooks allow Stripe to automatically notify your bot when payments happen.

### 3.1 Go to Stripe Webhooks

1. **Open:** https://dashboard.stripe.com/test/webhooks
2. **Click:** "+ Add endpoint" button (top right)

### 3.2 Configure Webhook Endpoint

For now, we'll use a test URL. After deploying your bot to a server, you'll update this.

**Endpoint URL:** Enter one of these:
- If testing locally: `http://localhost:5000/stripe-webhook`
- If deploying later: `https://your-domain.com/stripe-webhook`
- Temporary: `https://example.com/stripe/webhook` (will update later)

### 3.3 Select Events to Listen For

Click "Select events" and choose these **5 important events**:

1. ✅ `checkout.session.completed` - When payment succeeds
2. ✅ `customer.subscription.created` - New subscription
3. ✅ `customer.subscription.updated` - Subscription changed
4. ✅ `customer.subscription.deleted` - Subscription cancelled
5. ✅ `invoice.payment_succeeded` - Recurring payment successful
6. ✅ `invoice.payment_failed` - Payment failed (optional but helpful)

### 3.4 Save and Get Signing Secret

1. **Click:** "Add endpoint"
2. You'll see your new webhook endpoint
3. **Click:** "Reveal" next to "Signing secret"
4. **Copy** the webhook secret (starts with `whsec_`)
5. **Save it** - you'll need this next!

---

## ⏳ Step 4: Get Your API Keys (5 minutes)

### 4.1 Navigate to API Keys

1. **Open:** https://dashboard.stripe.com/test/apikeys
2. You'll see two keys:

### 4.2 Copy Your Keys

**Publishable Key:**
- Starts with `pk_test_`
- Already visible
- **Copy it** ✅

**Secret Key:**
1. Click **"Reveal test key"** button
2. Starts with `sk_test_`
3. **Copy it** ✅
4. ⚠️ **Keep this secret!** Never share or commit to GitHub

---

## 🔧 Step 5: Configure Your Bot (5 minutes)

### 5.1 Create .env File

1. **Navigate to:** `C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\`
2. **Create a file named:** `.env` (copy from `.env.template`)
3. **Fill in your keys:**

```env
# Paste your keys here (replace YOUR_SECRET_KEY_HERE with actual values)
STRIPE_SECRET_KEY=sk_test_PASTE_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_PASTE_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_PASTE_YOUR_WEBHOOK_SECRET_HERE

# These are already set (don't change)
STRIPE_PRICE_PREMIUM=price_1SbBRDCoLBi6DM3OWh4JR3Lt
STRIPE_PRICE_VIP=price_1SbBd5CoLBi6DM3OF8H2HKY8
```

### 5.2 Install Required Package

Run in your terminal:

```bash
pip install stripe python-dotenv
```

---

## ✅ Step 6: Verify Setup (5 minutes)

### 6.1 Test Payment Handler

Run this command to verify Stripe is configured:

```bash
cd C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting
python payment_handler.py
```

**Expected output:**
```
Stripe Available: True
Stripe Enabled: True
✅ Stripe configured and ready!
```

### 6.2 Start Your Bot

```bash
python telegram_bot.py
```

### 6.3 Test in Telegram

1. Open your bot in Telegram
2. Send `/subscribe`
3. You should see Premium and VIP options
4. Click on a tier to get payment link
5. Use Stripe test card: `4242 4242 4242 4242` (any future date, any CVC)

---

## 📋 Quick Reference - Your Stripe Details

Copy these for easy reference:

```
✅ Premium Price ID:  price_1SbBRDCoLBi6DM3OWh4JR3Lt
✅ VIP Price ID:      price_1SbBd5CoLBi6DM3OF8H2HKY8
⏳ Secret Key:        sk_test___________________ (get from Stripe)
⏳ Publishable Key:   pk_test___________________ (get from Stripe)
⏳ Webhook Secret:    whsec_____________________ (get from Stripe)
```

---

## 🧪 Testing Your Payment Flow

### Test Card Numbers

**Successful Payment:**
- Card: `4242 4242 4242 4242`
- Expiry: `12/25` (any future date)
- CVC: `123` (any 3 digits)
- ZIP: `12345` (any 5 digits)

**Declined Payment:**
- Card: `4000 0000 0000 0002`

### Test Steps

1. ✅ Send `/subscribe` in Telegram
2. ✅ Click Premium or VIP button
3. ✅ Click payment link
4. ✅ Fill in test card: `4242 4242 4242 4242`
5. ✅ Complete payment
6. ✅ Verify you get upgraded in bot

---

## 🚀 Going Live (Later)

When ready for real payments:

### Switch to Live Mode

1. **Activate account:** Complete Stripe verification
2. **Toggle to Live mode:** Top-right in Stripe Dashboard
3. **Get live keys:** Replace `sk_test_` with `sk_live_`
4. **Recreate webhook:** With your production URL
5. **Update .env:** Use live keys instead of test keys

---

## 🆘 Troubleshooting

### Issue: "Stripe not configured"

**Solution:** Make sure `.env` file exists with correct keys

### Issue: "Module not found: stripe"

**Solution:** Run `pip install stripe`

### Issue: Webhook not receiving events

**Solution:** 
1. Verify webhook URL is correct
2. Check webhook secret matches
3. For local testing, use ngrok: `ngrok http 5000`

### Issue: Payment succeeds but user not upgraded

**Solution:**
1. Check webhook is configured
2. Verify telegram_bot.py has webhook handler
3. Check logs for errors

---

## 📞 Need Help?

- **Stripe Docs:** https://stripe.com/docs
- **Stripe Support:** https://support.stripe.com
- **Test Cards:** https://stripe.com/docs/testing

---

## 🎉 When Complete

You'll be able to:
- ✅ Accept real payments
- ✅ Automatically upgrade users
- ✅ Handle subscriptions
- ✅ Process recurring payments
- ✅ Manage cancellations

**Let's make money! 💰🚀**



