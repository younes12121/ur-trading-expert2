"""
Upgrade Path Manager
Handles smart upgrade triggers, personalized messaging, and conversion optimization
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from enum import Enum

# Admin check for upgrade bypass
ADMIN_USER_IDS = [7713994326]  # Admin account - FULL ACCESS

def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    return telegram_id in ADMIN_USER_IDS

class TriggerType(Enum):
    """Types of upgrade triggers"""
    DAILY_LIMIT_REACHED = "daily_limit"
    RESTRICTED_ASSET = "restricted_asset"
    ADVANCED_FEATURE = "advanced_feature"
    ANALYTICS_REQUEST = "analytics_request"
    HIGH_ENGAGEMENT = "high_engagement"
    MULTIPLE_DAYS_ACTIVE = "multiple_days"
    WEEKEND_ACTIVITY = "weekend_activity"
    FIRST_WEEK_MILESTONE = "first_week"
    MONTHLY_SUMMARY = "monthly_summary"
    TRIAL_EXPIRING = "trial_expiring"
    PREMIUM_RENEWAL = "premium_renewal"

class UpgradePathManager:
    """Manages upgrade paths, triggers, and personalized messaging"""
    
    def __init__(self, data_file="upgrade_tracking.json"):
        self.data_file = data_file
        self.tracking = {}  # {telegram_id: user_tracking_data}
        self.load_data()
        
        # Trigger thresholds
        self.THRESHOLDS = {
            'high_engagement': 5,  # commands in 24 hours
            'multiple_days': 3,    # consecutive days active
            'first_week': 7,       # days since signup
            'monthly': 30          # days since signup
        }
    
    def load_data(self):
        """Load tracking data from JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.tracking = json.load(f)
            except:
                self.tracking = {}
    
    def save_data(self):
        """Save tracking data to JSON"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tracking, f, indent=2)
    
    def get_user_tracking(self, telegram_id: int) -> Dict:
        """Get or create user tracking data"""
        user_id_str = str(telegram_id)
        
        if user_id_str not in self.tracking:
            self.tracking[user_id_str] = {
                'telegram_id': telegram_id,
                'signup_date': datetime.now().strftime('%Y-%m-%d'),
                'commands_today': 0,
                'commands_this_week': 0,
                'last_command_date': None,
                'consecutive_days': 0,
                'upgrade_prompts_shown': 0,
                'last_upgrade_prompt': None,
                'trial_started': False,
                'trial_expiry': None,
                'restricted_assets_requested': [],
                'advanced_features_tried': [],
                'engagement_score': 0,
                'conversion_events': []
            }
            self.save_data()
        
        return self.tracking[user_id_str]
    
    def track_command(self, telegram_id: int, command: str, user_tier: str):
        """Track user command usage"""
        tracking = self.get_user_tracking(telegram_id)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset daily counter if new day
        if tracking['last_command_date'] != today:
            tracking['commands_today'] = 0
            tracking['last_command_date'] = today
        
        tracking['commands_today'] += 1
        tracking['commands_this_week'] += 1
        tracking['last_command_date'] = today
        
        # Update consecutive days
        if tracking['last_command_date'] == today:
            tracking['consecutive_days'] += 1
        
        # Calculate engagement score
        tracking['engagement_score'] = self._calculate_engagement_score(tracking)
        
        self.save_data()
    
    def _calculate_engagement_score(self, tracking: Dict) -> int:
        """Calculate user engagement score (0-100)"""
        score = 0
        
        # Daily activity (0-30 points)
        score += min(tracking.get('commands_today', 0) * 5, 30)
        
        # Weekly activity (0-25 points)
        score += min(tracking.get('commands_this_week', 0) * 2, 25)
        
        # Consecutive days (0-20 points)
        score += min(tracking.get('consecutive_days', 0) * 3, 20)
        
        # Days since signup (0-15 points)
        try:
            signup = datetime.strptime(tracking.get('signup_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
            days_active = (datetime.now() - signup).days
            score += min(days_active, 15)
        except:
            pass
        
        # Feature exploration (0-10 points)
        score += min(len(tracking.get('advanced_features_tried', [])) * 2, 10)
        
        return min(score, 100)
    
    def check_upgrade_triggers(self, telegram_id: int, user_tier: str, context: Dict) -> Optional[TriggerType]:
        """Check if any upgrade trigger should fire
        
        Args:
            telegram_id: User's Telegram ID
            user_tier: Current user tier ('free', 'premium', 'vip')
            context: Context dict with trigger info (command, asset, feature, etc.)
        
        Returns:
            TriggerType if trigger should fire, None otherwise
        """
        tracking = self.get_user_tracking(telegram_id)

        # Don't show prompts to admins (they have everything free)
        if is_admin(telegram_id):
            return None

        # Don't show prompts to VIP users
        if user_tier == 'vip':
            return None
        
        # Don't spam - limit prompts
        last_prompt = tracking.get('last_upgrade_prompt')
        if last_prompt:
            try:
                last_prompt_date = datetime.strptime(last_prompt, '%Y-%m-%d %H:%M:%S')
                hours_since = (datetime.now() - last_prompt_date).total_seconds() / 3600
                if hours_since < 6:  # Don't show more than once per 6 hours
                    return None
            except:
                pass
        
        # High-intent triggers (show immediately)
        if user_tier == 'free':
            # Daily limit reached
            if context.get('daily_limit_reached'):
                return TriggerType.DAILY_LIMIT_REACHED
            
            # Restricted asset requested
            if context.get('restricted_asset'):
                return TriggerType.RESTRICTED_ASSET
            
            # Advanced feature tried
            if context.get('advanced_feature'):
                feature = context.get('feature_name', '')
                if feature not in tracking.get('advanced_features_tried', []):
                    tracking['advanced_features_tried'].append(feature)
                    self.save_data()
                return TriggerType.ADVANCED_FEATURE
            
            # Analytics request
            if context.get('analytics_request'):
                return TriggerType.ANALYTICS_REQUEST
        
        # Medium-intent triggers (soft upsell)
        if user_tier == 'free':
            # High engagement
            if tracking.get('commands_today', 0) >= self.THRESHOLDS['high_engagement']:
                return TriggerType.HIGH_ENGAGEMENT
            
            # Multiple days active
            if tracking.get('consecutive_days', 0) >= self.THRESHOLDS['multiple_days']:
                return TriggerType.MULTIPLE_DAYS_ACTIVE
            
            # Weekend activity
            if datetime.now().weekday() >= 5:  # Saturday or Sunday
                if tracking.get('commands_today', 0) > 0:
                    return TriggerType.WEEKEND_ACTIVITY
        
        # Low-intent triggers (educational)
        if user_tier == 'free':
            # First week milestone
            try:
                signup = datetime.strptime(tracking.get('signup_date'), '%Y-%m-%d')
                days_since = (datetime.now() - signup).days
                if days_since == self.THRESHOLDS['first_week']:
                    return TriggerType.FIRST_WEEK_MILESTONE
            except:
                pass
        
        # Premium → VIP triggers
        if user_tier == 'premium':
            # Trial expiring (if on trial)
            if tracking.get('trial_started') and tracking.get('trial_expiry'):
                try:
                    expiry = datetime.strptime(tracking['trial_expiry'], '%Y-%m-%d')
                    days_remaining = (expiry - datetime.now()).days
                    if 0 <= days_remaining <= 2:
                        return TriggerType.TRIAL_EXPIRING
                except:
                    pass
            
            # High engagement Premium user (potential VIP candidate)
            if tracking.get('engagement_score', 0) > 70:
                # Check if user has been Premium for 2+ weeks
                try:
                    signup = datetime.strptime(tracking.get('signup_date'), '%Y-%m-%d')
                    days_since_signup = (datetime.now() - signup).days
                    if days_since_signup >= 14:
                        # Show VIP upgrade occasionally (not every time)
                        if tracking.get('upgrade_prompts_shown', 0) < 3:
                            return TriggerType.PREMIUM_RENEWAL
                except:
                    pass
            
            # Premium user using advanced features frequently
            if len(tracking.get('advanced_features_tried', [])) >= 3:
                # Show VIP upgrade after using multiple premium features
                if tracking.get('upgrade_prompts_shown', 0) < 2:
                    return TriggerType.PREMIUM_RENEWAL
        
        return None
    
    def get_upgrade_message(self, trigger_type: TriggerType, telegram_id: int, user_tier: str, context: Dict = None) -> Tuple[str, Dict]:
        """Get personalized upgrade message for trigger
        
        Returns:
            (message_text, keyboard_buttons)
        """
        tracking = self.get_user_tracking(telegram_id)
        context = context or {}
        
        # Update prompt tracking
        tracking['upgrade_prompts_shown'] = tracking.get('upgrade_prompts_shown', 0) + 1
        tracking['last_upgrade_prompt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_data()
        
        if user_tier == 'free':
            return self._get_free_to_premium_message(trigger_type, tracking, context)
        elif user_tier == 'premium':
            return self._get_premium_to_vip_message(trigger_type, tracking, context)
        
        return ("", {})
    
    def _get_free_to_premium_message(self, trigger_type: TriggerType, tracking: Dict, context: Dict) -> Tuple[str, Dict]:
        """Get Free → Premium upgrade message"""
        
        if trigger_type == TriggerType.DAILY_LIMIT_REACHED:
            msg = """⏰ *Daily Limit Reached!*

You've used your 1 free signal today.

🔥 *Premium Unlocks:*
• Unlimited signals (no daily limit)
• All 15 assets (BTC, Gold, Futures, Forex)
• AI predictions (95%+ accuracy)
• Portfolio optimization tools

📈 Join 500+ Premium traders making better decisions!

💰 *Only $39/month* - Less than $1.30/day!"""
            
            keyboard = [
                [{"text": "🎁 Start 7-Day FREE Trial", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ View Premium Features", "callback_data": "upgrade_premium_info"}],
                [{"text": "❌ Maybe Later", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.RESTRICTED_ASSET:
            asset = context.get('asset_name', 'This asset')
            msg = f"""🔒 *{asset} Signals - Premium Feature*

{asset} analysis requires Premium tier.

💎 *Premium Includes:*
• {asset} + 14 other assets
• Unlimited signals
• AI predictions
• Advanced analytics
• Portfolio tools worth $200+

🎁 *Try FREE for 7 days* - No credit card required!"""
            
            keyboard = [
                [{"text": "🎁 Start Free Trial", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ See All Premium Features", "callback_data": "upgrade_premium_info"}],
                [{"text": "❌ Not Now", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.ADVANCED_FEATURE:
            feature = context.get('feature_name', 'This feature')
            msg = f"""🔒 *{feature} - Premium Feature*

{feature} requires Premium tier.

⭐ *Premium Unlocks:*
• {feature}
• Portfolio optimization (Modern Portfolio Theory)
• Market structure analysis
• Advanced risk management
• All 15 trading assets

💰 *$39/month* - Start free trial:"""
            
            keyboard = [
                [{"text": "🎁 Try Free for 7 Days", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ View All Features", "callback_data": "upgrade_premium_info"}],
                [{"text": "❌ Dismiss", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.HIGH_ENGAGEMENT:
            commands = tracking.get('commands_today', 0)
            msg = f"""🎯 *You're Very Active!*

You've used {commands} commands today. You're clearly serious about trading!

⭐ *Premium Unlocks:*
• All 15 trading assets
• Unlimited signals
• AI predictions
• Portfolio optimization
• Advanced analytics

💰 *Only $39/month* - Less than $1.30/day!

📊 *Your Current Usage:*
• Signals: {commands}
• Assets: 2 of 15
• Daily limit: 1 signal

🔥 *Premium Unlocks:*
• Unlimited signals
• 13 more assets
• AI predictions"""
            
            keyboard = [
                [{"text": "🎁 Start Free Trial", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ Compare Plans", "callback_data": "upgrade_compare"}],
                [{"text": "❌ Maybe Later", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.MULTIPLE_DAYS_ACTIVE:
            days = tracking.get('consecutive_days', 0)
            msg = f"""🔥 *You're Committed!*

You've been active for {days} consecutive days. That's dedication!

⭐ *Ready to unlock Premium?*

• All 15 assets
• Unlimited signals
• AI predictions
• Portfolio tools

🎁 *Start 7-day FREE trial* - No credit card required!"""
            
            keyboard = [
                [{"text": "🎁 Start Free Trial", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ See Features", "callback_data": "upgrade_premium_info"}],
                [{"text": "❌ Not Now", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.FIRST_WEEK_MILESTONE:
            msg = """🎉 *7 Days with UR Trading Expert!*

You've been using the bot for a week. Ready to unlock full potential?

⭐ *Premium Trial Includes:*
• All 15 assets (FREE for 7 days)
• Unlimited signals
• AI predictions
• Portfolio optimization tools

🎁 *No credit card required for trial!*

Start your free trial now:"""
            
            keyboard = [
                [{"text": "🎁 Start 7-Day Free Trial", "callback_data": "upgrade_trial"}],
                [{"text": "⭐ View Premium Features", "callback_data": "upgrade_premium_info"}],
                [{"text": "❌ Maybe Later", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        # Default message
        msg = """⭐ *Unlock Premium Features*

Premium includes:
• All 15 trading assets
• Unlimited signals
• AI predictions
• Portfolio tools

💰 $39/month - Start free trial:"""
        
        keyboard = [
            [{"text": "🎁 Start Free Trial", "callback_data": "upgrade_trial"}],
            [{"text": "⭐ See Features", "callback_data": "upgrade_premium_info"}],
            [{"text": "❌ Dismiss", "callback_data": "upgrade_dismiss"}]
        ]
        return (msg, keyboard)
    
    def _get_premium_to_vip_message(self, trigger_type: TriggerType, tracking: Dict, context: Dict) -> Tuple[str, Dict]:
        """Get Premium → VIP upgrade message"""
        
        if trigger_type == TriggerType.TRIAL_EXPIRING:
            msg = """⏰ *Trial Ending Soon!*

Your 7-day Premium trial is ending. Continue with Premium or upgrade to VIP?

👑 *VIP Includes:*
• All Premium features ($39 value)
• Broker integration (one-click trading)
• Private community
• Weekly live calls
• Custom signals

💰 *VIP: $129/month*
🎁 *Save 20% first month: UPGRADE20*"""
            
            keyboard = [
                [{"text": "👑 Upgrade to VIP", "callback_data": "upgrade_vip"}],
                [{"text": "⭐ Keep Premium", "callback_data": "upgrade_keep_premium"}],
                [{"text": "❌ Cancel", "callback_data": "upgrade_cancel"}]
            ]
            return (msg, keyboard)
        
        elif trigger_type == TriggerType.PREMIUM_RENEWAL:
            # Premium → VIP upgrade message
            engagement = tracking.get('engagement_score', 0)
            features_used = len(tracking.get('advanced_features_tried', []))
            
            msg = f"""👑 *Ready for VIP?*

You're an active Premium user! Upgrade to VIP for even more power:

🔥 *VIP Exclusive Benefits:*
• Broker integration (one-click trading)
• Private community (150+ traders)
• Weekly live analysis calls
• Custom signal requests
• Personal onboarding

💰 *Only $90 more/month*
🎁 *Save 20% first month: UPGRADE20*

*Your Premium Value:*
• Engagement Score: {engagement}/100
• Features Used: {features_used}
• You're clearly serious about trading!

Upgrade now to unlock the full potential:"""
            
            keyboard = [
                [{"text": "👑 Upgrade to VIP", "callback_data": "upgrade_vip"}],
                [{"text": "⭐ See VIP Benefits", "callback_data": "upgrade_vip_info"}],
                [{"text": "❌ Maybe Later", "callback_data": "upgrade_dismiss"}]
            ]
            return (msg, keyboard)
        
        # Default VIP upgrade message
        msg = """👑 *Unlock VIP Power*

You're already Premium! Upgrade to VIP for:

🔥 *VIP Exclusive:*
• Broker integration (one-click trading)
• Private community (150+ traders)
• Weekly live analysis calls
• Custom signal requests
• Personal onboarding

💰 *Only $90 more/month*
🎁 *Save 20% first month: UPGRADE20*"""
        
        keyboard = [
            [{"text": "👑 Upgrade to VIP", "callback_data": "upgrade_vip"}],
            [{"text": "⭐ See VIP Benefits", "callback_data": "upgrade_vip_info"}],
            [{"text": "❌ Not Now", "callback_data": "upgrade_dismiss"}]
        ]
        return (msg, keyboard)
    
    def start_trial(self, telegram_id: int, days: int = 7) -> bool:
        """Start free trial for user"""
        tracking = self.get_user_tracking(telegram_id)
        
        if tracking.get('trial_started'):
            return False  # Trial already used
        
        tracking['trial_started'] = True
        expiry = datetime.now() + timedelta(days=days)
        tracking['trial_expiry'] = expiry.strftime('%Y-%m-%d')
        self.save_data()
        
        return True
    
    def track_conversion_event(self, telegram_id: int, event_type: str, data: Dict = None):
        """Track conversion events (trial started, upgrade clicked, etc.)"""
        tracking = self.get_user_tracking(telegram_id)
        
        event = {
            'type': event_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': data or {}
        }
        
        tracking['conversion_events'] = tracking.get('conversion_events', [])
        tracking['conversion_events'].append(event)
        self.save_data()
    
    def get_user_stats(self, telegram_id: int) -> Dict:
        """Get user upgrade path statistics"""
        tracking = self.get_user_tracking(telegram_id)
        
        return {
            'engagement_score': tracking.get('engagement_score', 0),
            'commands_today': tracking.get('commands_today', 0),
            'consecutive_days': tracking.get('consecutive_days', 0),
            'upgrade_prompts_shown': tracking.get('upgrade_prompts_shown', 0),
            'trial_started': tracking.get('trial_started', False),
            'days_since_signup': (datetime.now() - datetime.strptime(tracking.get('signup_date'), '%Y-%m-%d')).days
        }
    
    def get_platform_stats(self) -> Dict:
        """Get platform-wide upgrade path statistics"""
        total_users = len(self.tracking)
        trials_started = sum(1 for t in self.tracking.values() if t.get('trial_started'))
        high_engagement = sum(1 for t in self.tracking.values() if t.get('engagement_score', 0) > 50)
        
        return {
            'total_tracked_users': total_users,
            'trials_started': trials_started,
            'trial_rate': round(trials_started / total_users * 100, 1) if total_users > 0 else 0,
            'high_engagement_users': high_engagement,
            'engagement_rate': round(high_engagement / total_users * 100, 1) if total_users > 0 else 0
        }


# Global instance
_upgrade_manager = None

def get_upgrade_manager() -> UpgradePathManager:
    """Get global upgrade path manager instance"""
    global _upgrade_manager
    if _upgrade_manager is None:
        _upgrade_manager = UpgradePathManager()
    return _upgrade_manager
