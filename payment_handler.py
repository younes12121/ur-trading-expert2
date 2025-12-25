"""
Payment Handler Module
Handles Stripe payment integration for subscriptions
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    print("⚠️ Warning: python-dotenv not installed. Install with: pip install python-dotenv")

# Note: Install with: pip install stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("⚠️ Warning: Stripe not installed. Install with: pip install stripe")

class PaymentHandler:
    """Manages Stripe payments and subscriptions"""
    
    def __init__(self, stripe_secret_key=None, webhook_secret=None):
        """Initialize Stripe with API key"""
        if not STRIPE_AVAILABLE:
            print("⚠️ Stripe library not available. Payment features disabled.")
            return
        
        # Get API key from environment or parameter
        self.stripe_secret_key = stripe_secret_key or os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = webhook_secret or os.getenv('STRIPE_WEBHOOK_SECRET')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        if self.stripe_secret_key and self.stripe_secret_key != 'your_stripe_secret_key_here':
            stripe.api_key = self.stripe_secret_key
            self.enabled = True
            print("✅ Stripe configured successfully!")
        else:
            print("⚠️ Stripe API key not configured. Set STRIPE_SECRET_KEY in .env file.")
            self.enabled = False
        
        # Price IDs (set these after creating products in Stripe Dashboard)
        self.price_ids = {
            'premium_monthly': os.getenv('STRIPE_PRICE_PREMIUM', 'price_1SbBRDCoLBi6DM3OWh4JR3Lt'),
            'vip_monthly': os.getenv('STRIPE_PRICE_VIP', 'price_1SbBd5CoLBi6DM3OF8H2HKY8'),
        }
        
        # Print configuration status
        if self.enabled:
            print(f"   Premium Price ID: {self.price_ids['premium_monthly']}")
            print(f"   VIP Price ID: {self.price_ids['vip_monthly']}")
            print(f"   Webhook configured: {'Yes ✅' if self.webhook_secret else 'No ⏳'}")
        
        # Global pricing with regional adjustments
        self.pricing = {
            'premium': {
                'monthly': 39.00,  # Base USD price (updated from $29)
                'currency': 'USD',
                'interval': 'month',
                'regional_pricing': {
                    'USD': 39.00,  # United States
                    'EUR': 36.00,  # Europe (adjusted for exchange rate)
                    'GBP': 31.00,  # United Kingdom
                    'JPY': 5700,   # Japan
                    'AUD': 57.00,  # Australia
                    'CAD': 53.00,  # Canada
                    'BRL': 195.00, # Brazil
                    'CNY': 280.00, # China
                    'INR': 3200,   # India
                    'MXN': 690.00  # Mexico
                },
                'features': [
                    'All 15 trading assets (Crypto, Gold, Futures, Forex)',
                    'Unlimited signal alerts',
                    'Full analytics + CSV export',
                    'Multi-timeframe analysis',
                    'Market news (/news command)',
                    'Risk calculator & correlation checking',
                    '🔥 Portfolio optimization (Modern Portfolio Theory)',
                    '🔥 Professional market structure analysis',
                    '🔥 Advanced portfolio risk analysis',
                    '🔥 Enhanced correlation matrix with insights',
                    'Educational content (350+ items)',
                    'AI predictions & sentiment analysis',
                    'Priority support'
                ]
            },
            'vip': {
                'monthly': 129.00,  # Base USD price (updated from $99)
                'currency': 'USD',
                'interval': 'month',
                'regional_pricing': {
                    'USD': 129.00,
                    'EUR': 120.00,
                    'GBP': 102.00,
                    'JPY': 18900,
                    'AUD': 185.00,
                    'CAD': 173.00,
                    'BRL': 645.00,
                    'CNY': 925.00,
                    'INR': 10700,
                    'MXN': 2320.00
                },
                'features': [
                    '✨ All Premium features ($39 value)',
                    '🔥 All 5 advanced premium commands',
                    'Private community access',
                    'Weekly live analysis calls',
                    'Custom signal requests',
                    'Broker integration (MT4/MT5/OANDA)',
                    'Early access to new features',
                    'Personal onboarding call',
                    '1-on-1 premium support',
                    'Custom portfolio optimization',
                    'Priority feature requests'
                ]
            }
        }
    
    # ============================================================================
    # CUSTOMER MANAGEMENT
    # ============================================================================
    
    def create_customer(self, telegram_id: int, email: str, username: str = None) -> Optional[str]:
        """Create a Stripe customer
        
        Returns:
            customer_id or None if failed
        """
        if not self.enabled or not STRIPE_AVAILABLE:
            return None
        
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    'telegram_id': telegram_id,
                    'username': username or 'N/A'
                }
            )
            return customer.id
        except Exception as e:
            print(f"❌ Error creating Stripe customer: {e}")
            return None
    
    def get_customer_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Find Stripe customer by Telegram ID"""
        if not self.enabled or not STRIPE_AVAILABLE:
            return None
        
        try:
            customers = stripe.Customer.list(limit=1)
            for customer in customers.auto_paging_iter():
                if customer.metadata.get('telegram_id') == str(telegram_id):
                    return customer
            return None
        except Exception as e:
            print(f"❌ Error fetching customer: {e}")
            return None
    
    # ============================================================================
    # SUBSCRIPTION MANAGEMENT
    # ============================================================================
    
    def create_checkout_session(self, telegram_id: int, tier: str, success_url: str, cancel_url: str) -> Optional[str]:
        """Create a Stripe Checkout session for subscription
        
        Args:
            telegram_id: User's Telegram ID
            tier: 'premium' or 'vip'
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled
        
        Returns:
            checkout_url or None if failed
        """
        if not self.enabled:
            print(f"❌ Stripe not enabled - self.enabled = {self.enabled}")
            return None
        
        if not STRIPE_AVAILABLE:
            print(f"❌ Stripe library not available - STRIPE_AVAILABLE = {STRIPE_AVAILABLE}")
            return None
        
        if tier not in ['premium', 'vip']:
            return None
        
        print(f"🔄 Creating checkout session for user {telegram_id}, tier: {tier}")
        print(f"   Enabled: {self.enabled}, Stripe Available: {STRIPE_AVAILABLE}")
        
        try:
            # Get or create customer
            customer = self.get_customer_by_telegram_id(telegram_id)
            if not customer:
                # Create new customer (email will be collected in checkout)
                customer_id = None
                print(f"   No existing customer, will create during checkout")
            else:
                customer_id = customer.id
                print(f"   Found existing customer: {customer_id}")
            
            # Create checkout session
            price_id = self.price_ids[f'{tier}_monthly']
            print(f"   Using price ID: {price_id}")
            
            # Determine payment methods based on region (can be enhanced with user location detection)
            payment_methods = self._get_payment_methods_for_region()
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=payment_methods,
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'telegram_id': telegram_id,
                    'tier': tier
                },
                subscription_data={
                    'metadata': {
                        'telegram_id': telegram_id,
                        'tier': tier
                    }
                },
                # Enable automatic tax collection
                automatic_tax={'enabled': True},
                # Allow promotion codes
                allow_promotion_codes=True
            )
            
            print(f"✅ Checkout session created successfully!")
            print(f"   Session URL: {session.url[:80]}...")
            return session.url
        except Exception as e:
            print(f"❌ Error creating checkout session: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_payment_link(self, tier: str) -> Optional[str]:
        """Create a simple payment link (alternative to checkout session)
        
        Returns:
            payment_link_url or None
        """
        if not self.enabled or not STRIPE_AVAILABLE:
            return None
        
        try:
            price_id = self.price_ids[f'{tier}_monthly']
            
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
            )
            
            return payment_link.url
        except Exception as e:
            print(f"❌ Error creating payment link: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not STRIPE_AVAILABLE:
            return False
        
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            print(f"❌ Error canceling subscription: {e}")
            return False
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        if not self.enabled or not STRIPE_AVAILABLE:
            return None
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except Exception as e:
            print(f"❌ Error retrieving subscription: {e}")
            return None
    
    # ============================================================================
    # WEBHOOK HANDLING
    # ============================================================================
    
    def verify_webhook_signature(self, payload: bytes, signature: str, webhook_secret: str) -> bool:
        """Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header
            webhook_secret: Webhook signing secret from Stripe
        
        Returns:
            True if signature is valid
        """
        if not self.enabled or not STRIPE_AVAILABLE:
            return False
        
        try:
            stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return True
        except Exception as e:
            print(f"❌ Webhook signature verification failed: {e}")
            return False
    
    def handle_webhook_event(self, event_type: str, event_data: Dict) -> Dict:
        """Handle Stripe webhook events
        
        Returns:
            Dict with action to take (e.g., {'action': 'activate_subscription', 'telegram_id': 123, 'tier': 'premium'})
        """
        result = {'action': None}
        
        if event_type == 'checkout.session.completed':
            # Payment successful, activate subscription
            session = event_data
            telegram_id = session['metadata'].get('telegram_id')
            tier = session['metadata'].get('tier')
            subscription_id = session.get('subscription')
            
            if telegram_id and tier:
                result = {
                    'action': 'activate_subscription',
                    'telegram_id': int(telegram_id),
                    'tier': tier,
                    'subscription_id': subscription_id
                }
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled or expired
            subscription = event_data
            telegram_id = subscription['metadata'].get('telegram_id')
            
            if telegram_id:
                result = {
                    'action': 'deactivate_subscription',
                    'telegram_id': int(telegram_id)
                }
        
        elif event_type == 'invoice.payment_failed':
            # Payment failed
            invoice = event_data
            subscription = invoice.get('subscription')
            
            if subscription:
                sub_obj = self.get_subscription(subscription)
                if sub_obj:
                    telegram_id = sub_obj['metadata'].get('telegram_id')
                    if telegram_id:
                        result = {
                            'action': 'payment_failed',
                            'telegram_id': int(telegram_id)
                        }
        
        elif event_type == 'customer.subscription.updated':
            # Subscription updated (e.g., tier change)
            subscription = event_data
            telegram_id = subscription['metadata'].get('telegram_id')
            tier = subscription['metadata'].get('tier')
            
            if telegram_id and tier:
                result = {
                    'action': 'update_subscription',
                    'telegram_id': int(telegram_id),
                    'tier': tier
                }
        
        return result
    
    # ============================================================================
    # PRICING & INFORMATION
    # ============================================================================
    
    def get_pricing_message(self, tier: str = None) -> str:
        """Get formatted pricing message
        
        Args:
            tier: 'premium', 'vip', or None for all tiers
        """
        if tier:
            info = self.pricing.get(tier)
            if not info:
                return "Invalid tier"
            
            msg = f"💎 **{tier.upper()} TIER**\n\n"
            msg += f"**Price:** ${info['monthly']:.2f}/{info['interval']}\n\n"
            msg += f"**Features:**\n"
            for feature in info['features']:
                msg += f"✅ {feature}\n"
            
            return msg
        
        # Show all tiers
        msg = "💰 **SUBSCRIPTION PLANS**\n\n"
        
        msg += "🆓 **FREE TIER**\n"
        msg += "• 2 Forex pairs (EUR/USD, GBP/USD)\n"
        msg += "• 1 signal per day\n"
        msg += "• Basic analytics\n\n"
        
        msg += "⭐ **PREMIUM - $39/month**\n"
        for feature in self.pricing['premium']['features']:
            msg += f"• {feature}\n"
        msg += "\n"
        
        msg += "💎 **VIP - $129/month**\n"
        for feature in self.pricing['vip']['features']:
            msg += f"• {feature}\n"
        
        return msg
    
    def get_trial_info(self) -> str:
        """Get trial information message"""
        return """
🎁 **7-DAY FREE TRIAL**

Try Premium features for FREE!

**Trial includes:**
✅ All 8 trading assets
✅ Unlimited signal alerts
✅ Full analytics access
✅ Educational content
✅ All premium features

**After trial:**
• Automatically converts to Premium ($39/mo)
• Cancel anytime during trial (no charge)
• One trial per user

Start your free trial with `/subscribe premium trial`
"""
    
    # ============================================================================
    # TESTING & DEMO
    # ============================================================================
    
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return self.enabled and STRIPE_AVAILABLE
    
    def get_test_mode_message(self) -> str:
        """Message for when in test/demo mode"""
        if not STRIPE_AVAILABLE:
            return "⚠️ Stripe library not installed. Install with: `pip install stripe`"
        elif not self.enabled:
            return "⚠️ Stripe not configured. Set STRIPE_SECRET_KEY environment variable."
        return "✅ Stripe configured and ready!"
    
    def _get_payment_methods_for_region(self, region: str = None) -> List[str]:
        """Get payment methods supported for a region
        
        Args:
            region: ISO country code (e.g., 'US', 'GB', 'NL', 'BR')
        
        Returns:
            List of Stripe payment method types
        """
        # Default payment methods (card is universal)
        methods = ['card']
        
        # Regional payment methods
        regional_methods = {
            'NL': ['card', 'ideal'],  # Netherlands - iDEAL
            'BE': ['card', 'bancontact'],  # Belgium - Bancontact
            'DE': ['card', 'sofort'],  # Germany - Sofort
            'BR': ['card', 'boleto'],  # Brazil - Boleto
            'MX': ['card', 'oxxo'],  # Mexico - OXXO
            'CN': ['card', 'alipay'],  # China - Alipay
            'SG': ['card', 'grabpay'],  # Singapore - GrabPay
        }
        
        if region and region in regional_methods:
            methods.extend(regional_methods[region])
        
        return methods
    
    def get_price_for_currency(self, tier: str, currency: str = 'USD') -> float:
        """Get price for a specific currency
        
        Args:
            tier: 'premium' or 'vip'
            currency: ISO currency code (USD, EUR, GBP, etc.)
        
        Returns:
            Price in specified currency
        """
        if tier not in self.pricing:
            return 0.0
        
        pricing_info = self.pricing[tier]
        regional_pricing = pricing_info.get('regional_pricing', {})
        
        return regional_pricing.get(currency, pricing_info['monthly'])
    
    def create_checkout_session_global(self, telegram_id: int, tier: str, 
                                      currency: str = 'USD', region: str = None,
                                      success_url: str = None, cancel_url: str = None) -> Optional[str]:
        """Create checkout session with global payment support
        
        Args:
            telegram_id: User's Telegram ID
            tier: 'premium' or 'vip'
            currency: ISO currency code
            region: ISO country code for regional payment methods
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
        
        Returns:
            checkout_url or None
        """
        if not self.enabled or not STRIPE_AVAILABLE:
            return None
        
        # Get price for currency
        price = self.get_price_for_currency(tier, currency)
        
        # Create price if needed (or use existing price IDs per currency)
        # For simplicity, using base price IDs - in production, create prices per currency
        price_id = self.price_ids[f'{tier}_monthly']
        
        # Get payment methods for region
        payment_methods = self._get_payment_methods_for_region(region)
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=payment_methods,
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                currency=currency.lower(),
                success_url=success_url or f"https://t.me/your_bot?start=success",
                cancel_url=cancel_url or f"https://t.me/your_bot?start=cancel",
                metadata={
                    'telegram_id': telegram_id,
                    'tier': tier,
                    'currency': currency,
                    'region': region or 'unknown'
                },
                automatic_tax={'enabled': True},
                allow_promotion_codes=True
            )
            
            return session.url
        except Exception as e:
            print(f"❌ Error creating global checkout session: {e}")
            return None


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Test payment handler
    handler = PaymentHandler()
    
    print(f"Stripe Available: {STRIPE_AVAILABLE}")
    print(f"Stripe Enabled: {handler.is_configured()}")
    print()
    
    # Show pricing
    print(handler.get_pricing_message())

