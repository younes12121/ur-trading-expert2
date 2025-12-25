
# STRIPE INTERNATIONAL CONFIGURATION SETUP
# Supporting 49 countries

## QUICK SETUP GUIDE

### 1. Enable International Support in Stripe Dashboard
1. Go to https://dashboard.stripe.com/settings/payments
2. Enable "International payments"
3. Add supported countries from the list below

### 2. Configure Products for Each Country
Run the following script to create country-specific products:

```bash
# 1. Install Stripe CLI and login
stripe login

# 2. Create products for each country using the generated config files
# See stripe_config/pricing/ directory for country-specific pricing
# Use the Stripe Dashboard to create products manually or use the API
```

### 3. Set Up Webhooks for All Countries
Configure webhooks to handle international payments:

```python
webhook_events = [
    'checkout.session.completed',
    'customer.subscription.created',
    'customer.subscription.updated',
    'customer.subscription.deleted',
    'invoice.payment_succeeded',
    'invoice.payment_failed',
]

webhook_endpoint = stripe.WebhookEndpoint.create(
    url="https://yourdomain.com/stripe/webhook",
    enabled_events=webhook_events,
)
```

### 4. Configure Tax Collection
Enable automatic tax collection for supported countries:

```python
# In your Stripe dashboard:
# Settings > Tax > Automatic tax collection
# Enable for all supported countries
```

## SUPPORTED COUNTRIES (49)

- United States (US) - USD - card, us_bank_account
- Canada (CA) - CAD - card, interac
- Mexico (MX) - MXN - card, oxxo
- United Kingdom (GB) - GBP - card, bacs_debit
- Germany (DE) - EUR - card, sepa_debit, sofort
- France (FR) - EUR - card, sepa_debit
- Italy (IT) - EUR - card, sepa_debit
- Spain (ES) - EUR - card, sepa_debit
- Netherlands (NL) - EUR - card, sepa_debit, ideal
- Belgium (BE) - EUR - card, sepa_debit
- Austria (AT) - EUR - card, sepa_debit, sofort
- Switzerland (CH) - CHF - card
- Sweden (SE) - SEK - card
- Norway (NO) - NOK - card
- Denmark (DK) - DKK - card
- Finland (FI) - EUR - card, sepa_debit
- Ireland (IE) - EUR - card, sepa_debit
- Portugal (PT) - EUR - card, sepa_debit
- Greece (GR) - EUR - card, sepa_debit
- Poland (PL) - PLN - card
- Czech Republic (CZ) - CZK - card
- Hungary (HU) - HUF - card
- Romania (RO) - RON - card
- Japan (JP) - JPY - card
- Australia (AU) - AUD - card
- New Zealand (NZ) - NZD - card
- Singapore (SG) - SGD - card, paynow
- Hong Kong (HK) - HKD - card, fps
- South Korea (KR) - KRW - card
- China (CN) - CNY - alipay, wechat_pay
- India (IN) - INR - card, upi
- Thailand (TH) - THB - card
- Malaysia (MY) - MYR - card, fpx
- Indonesia (ID) - IDR - card
- Philippines (PH) - PHP - card, gcash
- Vietnam (VN) - VND - card
- Taiwan (TW) - TWD - card
- Brazil (BR) - BRL - card, boleto
- Argentina (AR) - ARS - card
- Chile (CL) - CLP - card
- Colombia (CO) - COP - card
- Peru (PE) - PEN - card
- United Arab Emirates (AE) - AED - card
- Saudi Arabia (SA) - SAR - card
- Israel (IL) - ILS - card
- South Africa (ZA) - ZAR - card
- Egypt (EG) - EGP - card
- Turkey (TR) - TRY - card
- Russia (RU) - RUB - card


## CURRENCY SUPPORT (39 currencies)

USD, EUR, GBP, JPY, AUD, CAD, CHF, SEK, NOK, DKK, PLN, CZK, HUF, RON, SGD, HKD, KRW, CNY, INR, THB, MYR, IDR, PHP, VND, TWD, BRL, ARS, CLP, COP, PEN, AED, SAR, ILS, ZAR, EGP, TRY, RUB, MXN, NZD

## PAYMENT METHODS (16 methods)

- Credit/Debit Cards (card) - Fee: 2.9% + $0.30
- SEPA Direct Debit (sepa_debit) - Fee: €0.35
- Bacs Direct Debit (bacs_debit) - Fee: £0.35
- iDEAL (ideal) - Fee: €0.35
- SOFORT (sofort) - Fee: €0.35
- Interac (interac) - Fee: 1.5%
- ACH Bank Transfer (us_bank_account) - Fee: $0
- OXXO (oxxo) - Fee: 3.5%
- Boleto (boleto) - Fee: 3.5%
- Alipay (alipay) - Fee: 3.4% + ¥0.16
- WeChat Pay (wechat_pay) - Fee: 3.4% + ¥0.16
- PayNow (paynow) - Fee: 0.6%
- FPS (fps) - Fee: 0.4%
- UPI (upi) - Fee: ₹1.5
- FPX (fpx) - Fee: 0.6%
- GCash (gcash) - Fee: 2.5%


## NEXT STEPS

1. Complete Stripe account verification for international payments
2. Set up bank accounts for different currencies (if needed)
3. Configure tax settings for each country
4. Test payments in different countries
5. Monitor conversion rates and fees
6. Set up alerts for failed international payments

## COMPLIANCE REQUIREMENTS

- GDPR compliance for EU countries
- Local tax registration where required
- Currency exchange regulations
- Consumer protection laws
- Data residency requirements

## MONITORING & ANALYTICS

Track these metrics:
- Conversion rates by country
- Payment method preferences
- Currency conversion costs
- Chargeback rates by region
- Customer lifetime value by market

---

*Generated for UR Trading Expert Bot - Global Expansion*
