"""
Referral System Module
Manages referral codes, tracking, commissions, and payouts
"""

import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional

class ReferralManager:
    """Manages referral program with tracking and commissions"""
    
    def __init__(self, data_file="referral_data.json"):
        self.data_file = data_file
        self.data = {
            'referral_codes': {},  # {code: user_id}
            'user_referrals': {},  # {user_id: {code, referrals, earnings, payouts}}
            'commission_rate': 0.20,  # 20% commission for regular users
            'affiliate_rates': {
                'micro_influencer': 0.30,  # 30% for 5K-50K followers
                'mid_tier': 0.35,          # 35% for 50K-500K followers
                'macro': 0.40,             # 40% for 500K+ followers
                'broker_partner': 0.25     # 25% for broker partnerships
            },
            'minimum_payout': 50.00,  # $50 minimum payout
            'payout_methods': ['paypal', 'stripe', 'bank_transfer']
        }
        self.load_data()
    
    def load_data(self):
        """Load referral data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save referral data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    # ============================================================================
    # REFERRAL CODE GENERATION
    # ============================================================================
    
    def generate_referral_code(self, user_id: int, custom_code: str = None) -> str:
        """Generate unique referral code for user
        
        Args:
            user_id: User ID
            custom_code: Optional custom code (must be unique)
        
        Returns:
            Referral code
        """
        user_id_str = str(user_id)
        
        # Check if user already has a code
        if user_id_str in self.data['user_referrals']:
            return self.data['user_referrals'][user_id_str]['code']
        
        # Generate or use custom code
        if custom_code:
            code = custom_code.upper()
            if code in self.data['referral_codes']:
                return None  # Code already taken
        else:
            # Generate random 6-character code
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if code not in self.data['referral_codes']:
                    break
        
        # Register code
        self.data['referral_codes'][code] = user_id
        self.data['user_referrals'][user_id_str] = {
            'code': code,
            'referrals': [],  # List of referred user IDs
            'total_referrals': 0,
            'active_referrals': 0,  # Users with active subscriptions
            'total_earnings': 0.0,
            'pending_payout': 0.0,
            'paid_out': 0.0,
            'payouts': [],
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.save_data()
        return code
    
    def get_referral_code(self, user_id: int) -> Optional[str]:
        """Get user's referral code (generate if doesn't exist)"""
        user_id_str = str(user_id)
        if user_id_str in self.data['user_referrals']:
            return self.data['user_referrals'][user_id_str]['code']
        
        # Generate referral code if user doesn't have one
        return self.generate_referral_code(user_id)
    
    # ============================================================================
    # REFERRAL TRACKING
    # ============================================================================
    
    def apply_referral_code(self, new_user_id: int, referral_code: str) -> bool:
        """Apply referral code to new user
        
        Args:
            new_user_id: New user signing up
            referral_code: Referral code used
        
        Returns:
            True if successful
        """
        code = referral_code.upper()
        
        # Check if code exists
        if code not in self.data['referral_codes']:
            return False
        
        referrer_id = self.data['referral_codes'][code]
        referrer_id_str = str(referrer_id)
        
        # Can't refer yourself
        if referrer_id == new_user_id:
            return False
        
        # Add to referrer's list
        if new_user_id not in self.data['user_referrals'][referrer_id_str]['referrals']:
            self.data['user_referrals'][referrer_id_str]['referrals'].append({
                'user_id': new_user_id,
                'joined_at': datetime.now().strftime('%Y-%m-%d'),
                'status': 'free',  # free, premium, vip
                'total_paid': 0.0,
                'commissions_earned': 0.0
            })
            self.data['user_referrals'][referrer_id_str]['total_referrals'] += 1
            self.save_data()
            return True
        
        return False
    
    def track_subscription_payment(self, user_id: int, amount: float, plan: str):
        """Track subscription payment for commission calculation
        
        Args:
            user_id: User who made payment
            amount: Payment amount
            plan: Subscription plan (premium/vip)
        """
        # Find who referred this user
        referrer_id = None
        for ref_id_str, data in self.data['user_referrals'].items():
            for referral in data['referrals']:
                if referral['user_id'] == user_id:
                    referrer_id = int(ref_id_str)
                    referral['status'] = plan
                    referral['total_paid'] += amount
                    break
            if referrer_id:
                break
        
        if not referrer_id:
            return  # User wasn't referred
        
        # Calculate commission
        commission = amount * self.data['commission_rate']
        
        referrer_id_str = str(referrer_id)
        ref_data = self.data['user_referrals'][referrer_id_str]
        
        # Update referral info
        for referral in ref_data['referrals']:
            if referral['user_id'] == user_id:
                referral['commissions_earned'] += commission
                break
        
        # Update referrer earnings
        ref_data['total_earnings'] += commission
        ref_data['pending_payout'] += commission
        
        # Update active referrals count
        ref_data['active_referrals'] = sum(
            1 for r in ref_data['referrals'] if r['status'] in ['premium', 'vip']
        )
        
        self.save_data()
    
    # ============================================================================
    # PAYOUTS
    # ============================================================================
    
    def request_payout(self, user_id: int, method: str, details: str) -> bool:
        """Request payout of earned commissions
        
        Args:
            user_id: User requesting payout
            method: Payment method (paypal, stripe, etc.)
            details: Payment details (email, etc.)
        
        Returns:
            True if request created
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.data['user_referrals']:
            return False
        
        ref_data = self.data['user_referrals'][user_id_str]
        
        # Check minimum payout ($50)
        if ref_data['pending_payout'] < 50:
            return False
        
        # Create payout request
        payout = {
            'amount': ref_data['pending_payout'],
            'method': method,
            'details': details,
            'requested_at': datetime.now().strftime('%Y-%m-%d'),
            'status': 'pending',  # pending, processing, completed, failed
            'completed_at': None
        }
        
        ref_data['payouts'].append(payout)
        self.save_data()
        return True
    
    def complete_payout(self, user_id: int, payout_index: int):
        """Mark payout as completed (admin function)
        
        Args:
            user_id: User ID
            payout_index: Index in payouts list
        """
        user_id_str = str(user_id)
        ref_data = self.data['user_referrals'][user_id_str]
        
        if payout_index < len(ref_data['payouts']):
            payout = ref_data['payouts'][payout_index]
            payout['status'] = 'completed'
            payout['completed_at'] = datetime.now().strftime('%Y-%m-%d')
            
            # Move from pending to paid out
            amount = payout['amount']
            ref_data['pending_payout'] -= amount
            ref_data['paid_out'] += amount
            
            self.save_data()
    
    # ============================================================================
    # STATISTICS & DISPLAY
    # ============================================================================
    
    def get_referral_stats(self, user_id: int) -> Optional[Dict]:
        """Get referral statistics for user"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.data['user_referrals']:
            return None
        
        return self.data['user_referrals'][user_id_str]
    
    def format_referral_message(self, user_id: int) -> str:
        """Format referral dashboard message"""
        stats = self.get_referral_stats(user_id)
        
        if not stats:
            code = self.generate_referral_code(user_id)
            msg = f"💰 **REFERRAL PROGRAM**\n\n"
            msg += f"*Your Referral Code:* `{code}`\n\n"
            msg += "🎁 *Earn 20% Commission!*\n\n"
            msg += "How it works:\n"
            msg += "1. Share your code with friends\n"
            msg += "2. They subscribe using your code\n"
            msg += "3. You earn 20% of their payment\n"
            msg += "4. Commission paid monthly via PayPal/Stripe\n\n"
            msg += "*Minimum Payout:* $50\n"
            msg += "*Payment Schedule:* Monthly (1st of month)\n\n"
            msg += "Start sharing and earning! 🚀"
            return msg
        
        code = stats['code']
        total_refs = stats['total_referrals']
        active_refs = stats['active_referrals']
        earnings = stats['total_earnings']
        pending = stats['pending_payout']
        paid = stats['paid_out']
        
        msg = f"💰 **YOUR REFERRAL DASHBOARD**\n\n"
        msg += f"*Your Code:* `{code}`\n\n"
        
        msg += "📊 *Statistics:*\n"
        msg += f"Total Referrals: {total_refs}\n"
        msg += f"Active Subscribers: {active_refs}\n\n"
        
        msg += "💵 *Earnings:*\n"
        msg += f"Total Earned: ${earnings:.2f}\n"
        msg += f"Pending Payout: ${pending:.2f}\n"
        msg += f"Already Paid: ${paid:.2f}\n\n"
        
        if pending >= 50:
            msg += "✅ *You can request a payout!*\n"
            msg += "`/referral payout [paypal/stripe] [email]`\n\n"
        else:
            msg += f"⏳ *${50 - pending:.2f} until minimum payout*\n\n"
        
        # Show top referrals
        if stats['referrals']:
            msg += "*Top Referrals:*\n"
            sorted_refs = sorted(stats['referrals'], key=lambda x: x['commissions_earned'], reverse=True)[:5]
            for ref in sorted_refs:
                status_emoji = {'free': '🆓', 'premium': '⭐', 'vip': '👑'}.get(ref['status'], '')
                msg += f"{status_emoji} User #{ref['user_id']} - ${ref['commissions_earned']:.2f}\n"
            msg += "\n"
        
        msg += "*Commands:*\n"
        msg += "`/referral share` - Get share message\n"
        msg += "`/referral stats` - Detailed stats\n"
        msg += "`/referral payout` - Request payout\n"
        
        return msg
    
    def get_share_message(self, user_id: int) -> str:
        """Get referral share message"""
        code = self.get_referral_code(user_id)
        
        if not code:
            code = self.generate_referral_code(user_id)
        
        msg = f"🚀 **Join the #1 Trading Signal Bot!**\n\n"
        msg += "Get A+ trading signals with 20-criteria analysis:\n"
        msg += "✅ Ultra-filtered signals (18-20/20 score)\n"
        msg += "✅ Multi-timeframe confirmation\n"
        msg += "✅ Risk management tools\n"
        msg += "✅ Performance analytics\n"
        msg += "✅ Educational content\n\n"
        msg += f"*Use my referral code:* `{code}`\n\n"
        msg += "🎁 *7-Day Free Trial* - Try Premium free!\n\n"
        msg += "[Start Trading Smarter Today! 📈]"
        
        return msg
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top referrers leaderboard"""
        referrers = []
        
        for user_id_str, data in self.data['user_referrals'].items():
            referrers.append({
                'user_id': int(user_id_str),
                'code': data['code'],
                'total_referrals': data['total_referrals'],
                'active_referrals': data['active_referrals'],
                'total_earnings': data['total_earnings']
            })
        
        # Sort by total earnings
        sorted_referrers = sorted(referrers, key=lambda x: x['total_earnings'], reverse=True)
        return sorted_referrers[:limit]
    
    def format_leaderboard_message(self) -> str:
        """Format referral leaderboard message"""
        leaderboard = self.get_leaderboard(10)
        
        if not leaderboard:
            return "📊 No referrers yet. Be the first to earn commissions!"
        
        msg = "🏆 **REFERRAL LEADERBOARD**\n\n"
        msg += "*Top Earners This Month:*\n\n"
        
        for rank, referrer in enumerate(leaderboard, 1):
            rank_emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f"{rank}.")
            msg += f"{rank_emoji} Code `{referrer['code']}`\n"
            msg += f"   Referrals: {referrer['active_referrals']}/{referrer['total_referrals']}\n"
            msg += f"   Earned: ${referrer['total_earnings']:.2f}\n\n"
        
        msg += "💡 Share your code and climb the ranks!"
        
        return msg


if __name__ == "__main__":
    # Test referral system
    rm = ReferralManager()
    
    # Generate codes
    code1 = rm.generate_referral_code(12345)
    print(f"User 12345 code: {code1}")
    
    # Apply referral
    rm.apply_referral_code(54321, code1)
    
    # Track payment
    rm.track_subscription_payment(54321, 29, 'premium')
    
    # View stats
    print("\n" + rm.format_referral_message(12345))


















