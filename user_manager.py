"""
User Manager Module
Handles user tier management, feature access control, and subscription logic
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from functools import wraps

# Admin user IDs - get free access to all features
ADMIN_USER_IDS = [7713994326]  # Admin account - FULL ACCESS

def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    # Handle both int and string types for robustness
    telegram_id_int = int(telegram_id) if telegram_id else 0
    return telegram_id_int in ADMIN_USER_IDS

class UserManager:
    """Manages users, tiers, and feature access (JSON-based for now, will migrate to PostgreSQL)"""
    
    def __init__(self, data_file="users_data.json"):
        self.data_file = data_file
        self.users = {}  # {telegram_id: user_data}
        self.load_data()
    
    def load_data(self):
        """Load users from JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
    
    def save_data(self):
        """Save users to JSON"""
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================
    
    def get_user(self, telegram_id: int) -> Dict:
        """Get or create user"""
        user_id_str = str(telegram_id)
        
        if user_id_str not in self.users:
            # Create new user with free tier
            self.users[user_id_str] = {
                'telegram_id': telegram_id,
                'tier': 'free',
                'subscription_date': None,
                'subscription_expiry': None,
                'trial_used': False,
                'capital': 500.0,
                'risk_per_trade': 1.0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_active': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'signals_used_today': 0,
                'last_signal_date': None
            }
            self.save_data()
        else:
            # Update last active
            self.users[user_id_str]['last_active'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_data()
        
        return self.users[user_id_str]
    
    def update_user_tier(self, telegram_id: int, tier: str, expiry_date: Optional[str] = None):
        """Update user tier
        
        Args:
            telegram_id: Telegram user ID
            tier: 'free', 'premium', or 'vip'
            expiry_date: Optional expiry date (YYYY-MM-DD)
        """
        user = self.get_user(telegram_id)
        user['tier'] = tier.lower()
        user['subscription_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if expiry_date:
            user['subscription_expiry'] = expiry_date
        elif tier in ['premium', 'vip']:
            # Default to 30 days from now
            expiry = datetime.now() + timedelta(days=30)
            user['subscription_expiry'] = expiry.strftime('%Y-%m-%d')
        
        self.save_data()
    
    def check_subscription_expiry(self, telegram_id: int) -> bool:
        """Check if subscription has expired and downgrade if needed
        
        Returns:
            True if subscription is active, False if expired
        """
        user = self.get_user(telegram_id)
        
        if user['tier'] == 'free':
            return True
        
        if not user['subscription_expiry']:
            return True
        
        try:
            expiry = datetime.strptime(user['subscription_expiry'], '%Y-%m-%d')
            if datetime.now() > expiry:
                # Subscription expired, downgrade to free
                user['tier'] = 'free'
                self.save_data()
                return False
        except:
            pass
        
        return True
    
    # ============================================================================
    # TIER CHECKING & FEATURE ACCESS
    # ============================================================================
    
    def get_user_tier(self, telegram_id: int) -> str:
        """Get user tier (admins are treated as VIP)"""
        # Admins get VIP tier automatically
        if is_admin(telegram_id):
            return 'vip'
        self.check_subscription_expiry(telegram_id)
        user = self.get_user(telegram_id)
        return user['tier']
    
    def set_user_tier(self, telegram_id: int, tier: str, expiry_date: Optional[str] = None):
        """Alias for update_user_tier for compatibility"""
        return self.update_user_tier(telegram_id, tier, expiry_date)
    
    def is_premium(self, telegram_id: int) -> bool:
        """Check if user has premium or VIP tier (admins always return True)"""
        if is_admin(telegram_id):
            return True
        tier = self.get_user_tier(telegram_id)
        return tier in ['premium', 'vip']
    
    def is_vip(self, telegram_id: int) -> bool:
        """Check if user has VIP tier (admins always return True)"""
        if is_admin(telegram_id):
            return True
        tier = self.get_user_tier(telegram_id)
        return tier == 'vip'
    
    def has_feature_access(self, telegram_id: int, feature: str) -> bool:
        """Check if user has access to a specific feature

        Features:
        - all_assets: Access to all 8 assets (vs 2 for free)
        - unlimited_alerts: No limit on signals per day
        - full_analytics: Full analytics and CSV export
        - mtf_analysis: Multi-timeframe analysis
        - risk_calculator: Advanced risk calculator
        - correlation_check: Correlation conflict checking
        - csv_export: Export trades to CSV
        - education_content: Access to educational content
        - sentiment_analysis: AI sentiment analysis
        - ai_predictions: ML success probability predictions
        - international: Access to international markets (CNY, BRL)
        - ultra_elite: Ultra Elite signals (95-98% win rate, Ultra Premium only)
        - quantum_elite: Quantum Elite signals (98%+ win rate, AI/ML powered, VIP only)
        - quantum_intraday: Quantum Intraday signals (85-92% win rate, Premium+ only)
        - broker_integration: Broker API integration (VIP only)
        - private_community: Private Discord/Telegram group (VIP only)
        - custom_signals: Request custom signal pairs (VIP only)
        - live_calls: Weekly live analysis calls (VIP only)
        - crypto: Access to crypto futures (ETH, BTC futures)
        """
        # Admins get free access to ALL features (including undefined ones)
        if is_admin(telegram_id):
            return True
        
        tier = self.get_user_tier(telegram_id)
        
        # Free tier features
        free_features = []
        
        # Premium tier features
        premium_features = [
            'all_assets',
            'unlimited_alerts',
            'full_analytics',
            'mtf_analysis',
            'risk_calculator',
            'correlation_check',
            'csv_export',
            'education_content',
            'sentiment_analysis',
            'ai_predictions',
            'international'  # Access to international markets (CNY, BRL)
        ]
        
        # VIP tier features (includes all premium + exclusive)
        vip_features = premium_features + [
            'ultra_elite',  # Ultra Elite signals (95-98% win rate)
            'quantum_elite',  # Quantum Elite signals (98%+ win rate, AI/ML powered)
            'quantum_intraday',  # Quantum Intraday signals (85-92% win rate)
            'broker_integration',
            'private_community',
            'custom_signals',
            'live_calls',
            'crypto'  # Access to crypto futures (ETH, BTC futures)
        ]
        
        if tier == 'vip':
            return feature in vip_features
        elif tier == 'premium':
            return feature in premium_features
        else:  # free
            return feature in free_features
    
    def get_allowed_assets(self, telegram_id: int) -> List[str]:
        """Get list of assets user can access (admins get all assets)"""
        if is_admin(telegram_id):
            return ['BTC', 'GOLD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'EURJPY', 'NZDUSD', 'USDCHF', 'ES', 'NQ', 'ETH']
        if self.has_feature_access(telegram_id, 'all_assets'):
            return ['BTC', 'GOLD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'EURJPY']
        else:
            # Free tier: Only EUR/USD and GBP/USD
            return ['EURUSD', 'GBPUSD']
    
    def check_daily_signal_limit(self, telegram_id: int) -> tuple:
        """Check if user can receive another signal today
        
        Returns:
            (can_receive, remaining, limit)
        """
        # Admins have unlimited signals
        if is_admin(telegram_id):
            return (True, -1, -1)  # -1 means unlimited
        
        user = self.get_user(telegram_id)
        
        # Premium/VIP have unlimited
        if self.has_feature_access(telegram_id, 'unlimited_alerts'):
            return (True, -1, -1)  # -1 means unlimited
        
        # Free tier: 1 signal per day
        limit = 1
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset counter if it's a new day
        if user.get('last_signal_date') != today:
            user['signals_used_today'] = 0
            user['last_signal_date'] = today
            self.save_data()
        
        used = user.get('signals_used_today', 0)
        can_receive = used < limit
        remaining = max(0, limit - used)
        
        return (can_receive, remaining, limit)
    
    def increment_daily_signals(self, telegram_id: int):
        """Increment daily signal counter"""
        user = self.get_user(telegram_id)
        today = datetime.now().strftime('%Y-%m-%d')
        
        if user.get('last_signal_date') != today:
            user['signals_used_today'] = 1
            user['last_signal_date'] = today
        else:
            user['signals_used_today'] = user.get('signals_used_today', 0) + 1
        
        self.save_data()
    
    # ============================================================================
    # TRIAL SYSTEM
    # ============================================================================
    
    def can_start_trial(self, telegram_id: int) -> bool:
        """Check if user can start a free trial"""
        user = self.get_user(telegram_id)
        return not user.get('trial_used', False) and user['tier'] == 'free'
    
    def start_trial(self, telegram_id: int, days: int = 7) -> bool:
        """Start a free trial
        
        Args:
            telegram_id: User ID
            days: Trial duration (default 7 days)
        
        Returns:
            True if trial started, False if already used
        """
        if not self.can_start_trial(telegram_id):
            return False
        
        user = self.get_user(telegram_id)
        expiry = datetime.now() + timedelta(days=days)
        
        user['tier'] = 'premium'
        user['trial_used'] = True
        user['subscription_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user['subscription_expiry'] = expiry.strftime('%Y-%m-%d')
        
        self.save_data()
        return True
    
    # ============================================================================
    # UPGRADE MESSAGES
    # ============================================================================
    
    def get_upgrade_message(self, feature: str) -> str:
        """Get upgrade message for a specific feature"""
        messages = {
            'all_assets': "🔒 *PREMIUM FEATURE*\n\nAccess to all 15 trading assets (BTC, Gold, Futures, Forex) requires Premium or VIP tier.\n\n*Free Tier:* EUR/USD, GBP/USD only\n*Premium ($39/mo):* All assets + advanced tools unlocked!\n\nUse `/subscribe` to upgrade.",
            
            'ultra_elite': "🔒 **ULTRA ELITE ACCESS REQUIRED**\n\nUltra Elite signals are available to Ultra Premium subscribers only.\n\n**Ultra Elite Features:**\n• 95-98% win rate target\n• Institutional-grade analysis\n• 19+/20 criteria + 5 confirmations\n• Ultra-rare perfect setups only\n\n💎 Upgrade to Ultra Premium: `/subscribe`",
            
            'quantum_elite': "🟣 **QUANTUM ELITE ACCESS REQUIRED**\n\nQuantum Elite signals are available to Ultra Premium subscribers only.\n\n**Quantum Elite Features:**\n• 98%+ win rate target\n• AI/ML powered predictions\n• Perfect 20/20 criteria + Ultra Elite + AI\n• Market regime analysis\n• Sentiment analysis\n• Perfect market structure\n• Extremely rare - once in a month setups\n\n💎 Upgrade to Ultra Premium: `/subscribe`",
            
            'quantum_intraday': "🟣 **QUANTUM INTRADAY ACCESS REQUIRED**\n\nQuantum Intraday signals are available to Premium subscribers and above.\n\n**Quantum Intraday Features:**\n• 85-92% win rate target\n• AI/ML powered predictions (90%+ confidence)\n• 15-18/20 criteria + Ultra Elite confirmations\n• Market regime analysis\n• Sentiment analysis\n• Session-based filtering\n• Valid for 1-4 hours\n\n💎 Upgrade to Premium: `/subscribe`",
            
            'unlimited_alerts': "🔒 *DAILY LIMIT REACHED*\n\nFree tier is limited to 1 signal per day.\n\n*Upgrade to Premium:* Unlimited signals + advanced portfolio tools!\n*Price:* $39/month\n\nUse `/subscribe` to upgrade.",
            
            'mtf_analysis': "🔒 *PREMIUM FEATURE*\n\nMulti-Timeframe Analysis requires Premium or VIP tier.\n\nThis powerful tool analyzes M15, H1, H4, and D1 timeframes to give you the best entry timing.\n\nUse `/subscribe` to unlock.",
            
            'full_analytics': "🔒 *PREMIUM FEATURE*\n\nFull analytics and performance tracking requires Premium or VIP tier.\n\n*Includes:*\n• Detailed win rate analysis\n• CSV export\n• Performance by pair/session\n• Custom reports\n\nUse `/subscribe` to upgrade.",
            
            'broker_integration': "🔒 *VIP EXCLUSIVE*\n\nBroker integration (one-click trading) is exclusive to VIP tier.\n\n*VIP Benefits ($129/mo):*\n• Direct broker connection\n• One-click trade execution\n• Auto position sizing\n• Paper trading mode\n• All 5 advanced premium tools\n• + All Premium features\n\nUse `/subscribe` to upgrade to VIP.",
            
            'private_community': "🔒 *VIP EXCLUSIVE*\n\nPrivate community access is exclusive to VIP members.\n\n*VIP Community:*\n• Private Discord/Telegram group\n• Weekly live analysis calls\n• Network with top traders\n• Priority support\n\nUse `/subscribe` to join VIP.",
        }
        
        return messages.get(feature, "🔒 This feature requires Premium or VIP tier. Use `/subscribe` to upgrade.")
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    
    def get_user_stats(self, telegram_id: int) -> Dict:
        """Get user statistics"""
        user = self.get_user(telegram_id)
        
        # Calculate days as member
        created = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
        days_member = (datetime.now() - created).days
        
        # Admins are treated as VIP
        tier = 'vip' if is_admin(telegram_id) else user['tier']
        
        stats = {
            'tier': tier,
            'days_member': days_member,
            'capital': user.get('capital', 500.0),
            'risk_per_trade': user.get('risk_per_trade', 1.0),
        }
        
        # Add subscription info if applicable (admins get VIP benefits)
        if tier in ['premium', 'vip'] or is_admin(telegram_id):
            if user['subscription_expiry']:
                try:
                    expiry = datetime.strptime(user['subscription_expiry'], '%Y-%m-%d')
                    days_remaining = (expiry - datetime.now()).days
                    stats['days_remaining'] = max(0, days_remaining)
                    stats['expires_on'] = user['subscription_expiry']
                except:
                    pass
        
        return stats
    
    def get_all_users_stats(self) -> Dict:
        """Get platform-wide user statistics"""
        total = len(self.users)
        free = sum(1 for u in self.users.values() if u['tier'] == 'free')
        premium = sum(1 for u in self.users.values() if u['tier'] == 'premium')
        vip = sum(1 for u in self.users.values() if u['tier'] == 'vip')
        
        # Active users (active in last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        active = 0
        for user in self.users.values():
            try:
                last_active = datetime.strptime(user['last_active'], '%Y-%m-%d %H:%M:%S')
                if last_active > week_ago:
                    active += 1
            except:
                pass
        
        return {
            'total_users': total,
            'free_users': free,
            'premium_users': premium,
            'vip_users': vip,
            'active_users_7d': active,
            'conversion_rate': round((premium + vip) / total * 100, 1) if total > 0 else 0
        }


# ============================================================================
# DECORATORS FOR FEATURE ACCESS
# ============================================================================

def require_tier(tier: str):
    """Decorator to require a specific tier for a command
    
    Usage:
        @require_tier('premium')
        async def premium_command(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_manager = UserManager()
            telegram_id = update.effective_user.id
            user_tier = user_manager.get_user_tier(telegram_id)
            
            # Check tier hierarchy
            tier_hierarchy = {'free': 0, 'premium': 1, 'vip': 2}
            required_level = tier_hierarchy.get(tier.lower(), 0)
            user_level = tier_hierarchy.get(user_tier, 0)
            
            if user_level < required_level:
                # Send upgrade message
                msg = f"🔒 This command requires **{tier.upper()}** tier or higher.\n\n"
                msg += f"Your current tier: **{user_tier.upper()}**\n\n"
                msg += "Use `/subscribe` to upgrade and unlock all features!"
                await update.message.reply_text(msg, parse_mode='Markdown')
                return
            
            # User has access, execute command
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature: str):
    """Decorator to require a specific feature access
    
    Usage:
        @require_feature('mtf_analysis')
        async def mtf_command(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_manager = UserManager()
            telegram_id = update.effective_user.id
            
            if not user_manager.has_feature_access(telegram_id, feature):
                # Send upgrade message
                msg = user_manager.get_upgrade_message(feature)
                await update.message.reply_text(msg, parse_mode='Markdown')
                return
            
            # User has access, execute command
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test user manager
    um = UserManager()
    
    # Test user creation
    user = um.get_user(123456789)
    print(f"User: {user}")
    
    # Test tier checking
    print(f"Is premium: {um.is_premium(123456789)}")
    print(f"Has MTF access: {um.has_feature_access(123456789, 'mtf_analysis')}")
    
    # Test upgrade
    um.update_user_tier(123456789, 'premium')
    print(f"After upgrade - Is premium: {um.is_premium(123456789)}")
    
    # Test stats
    stats = um.get_all_users_stats()
    print(f"Platform stats: {stats}")

