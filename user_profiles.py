"""
User Profiles Module
Manages user profiles, badges, achievements, and privacy settings
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List

class UserProfileManager:
    """Manages user profiles and public statistics"""
    
    def __init__(self, data_file="user_profiles.json"):
        self.data_file = data_file
        self.profiles = {}
        self.load_data()
    
    def load_data(self):
        """Load profiles from JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = {}
    
    def save_data(self):
        """Save profiles to JSON"""
        with open(self.data_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    # ============================================================================
    # PROFILE MANAGEMENT
    # ============================================================================
    
    def get_profile(self, telegram_id: int) -> Dict:
        """Get or create user profile"""
        user_id_str = str(telegram_id)
        
        if user_id_str not in self.profiles:
            # Create new profile
            self.profiles[user_id_str] = {
                'telegram_id': telegram_id,
                'username': None,
                'display_name': None,
                'bio': None,
                'joined_date': datetime.now().strftime('%Y-%m-%d'),
                
                # Privacy settings
                'privacy': {
                    'profile_public': True,
                    'show_win_rate': True,
                    'show_trades': True,
                    'show_pnl': False,  # P&L private by default
                    'allow_followers': True,
                    'show_in_leaderboard': True
                },
                
                # Trading stats
                'stats': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'total_pips': 0.0,
                    'total_pnl': 0.0,
                    'best_trade': 0.0,
                    'worst_trade': 0.0,
                    'current_streak': 0,
                    'best_streak': 0,
                    'trades_this_month': 0
                },
                
                # Badges and achievements
                'badges': [],
                'achievements': [],
                
                # Social
                'followers': [],
                'following': [],
                'blocked_users': []
            }
            self.save_data()
        
        return self.profiles[user_id_str]
    
    def update_profile(self, telegram_id: int, **kwargs):
        """Update profile fields"""
        profile = self.get_profile(telegram_id)
        
        # Update allowed fields
        allowed_fields = ['username', 'display_name', 'bio']
        for field, value in kwargs.items():
            if field in allowed_fields:
                profile[field] = value
        
        self.save_data()
    
    def update_privacy_settings(self, telegram_id: int, setting: str, value: bool):
        """Update privacy setting"""
        profile = self.get_profile(telegram_id)
        
        if setting in profile['privacy']:
            profile['privacy'][setting] = value
            self.save_data()
            return True
        return False
    
    def is_profile_public(self, telegram_id: int) -> bool:
        """Check if profile is public"""
        profile = self.get_profile(telegram_id)
        return profile['privacy'].get('profile_public', False)
    
    def can_view_profile(self, viewer_id: int, profile_owner_id: int) -> bool:
        """Check if viewer can see profile"""
        # Own profile always visible
        if viewer_id == profile_owner_id:
            return True
        
        # Check if profile is public
        owner_profile = self.get_profile(profile_owner_id)
        if not owner_profile['privacy'].get('profile_public', False):
            return False
        
        # Check if blocked
        if viewer_id in owner_profile.get('blocked_users', []):
            return False
        
        return True
    
    # ============================================================================
    # TRADING STATISTICS
    # ============================================================================
    
    def update_trade_stats(self, telegram_id: int, trade_result: Dict):
        """Update trading statistics after a trade
        
        Args:
            telegram_id: User ID
            trade_result: Dict with 'won' (bool), 'pips' (float), 'pnl' (float)
        """
        profile = self.get_profile(telegram_id)
        stats = profile['stats']
        
        # Update totals
        stats['total_trades'] += 1
        stats['trades_this_month'] += 1
        
        if trade_result['won']:
            stats['winning_trades'] += 1
            stats['current_streak'] = max(0, stats['current_streak']) + 1
        else:
            stats['losing_trades'] += 1
            stats['current_streak'] = min(0, stats['current_streak']) - 1
        
        # Update best streak
        if abs(stats['current_streak']) > abs(stats['best_streak']):
            stats['best_streak'] = stats['current_streak']
        
        # Update win rate
        if stats['total_trades'] > 0:
            stats['win_rate'] = round((stats['winning_trades'] / stats['total_trades']) * 100, 1)
        
        # Update pips and P&L
        stats['total_pips'] += trade_result.get('pips', 0)
        stats['total_pnl'] += trade_result.get('pnl', 0)
        
        # Update best/worst trade
        pnl = trade_result.get('pnl', 0)
        if pnl > stats['best_trade']:
            stats['best_trade'] = pnl
        if pnl < stats['worst_trade']:
            stats['worst_trade'] = pnl
        
        self.save_data()
        
        # Check for achievements
        self._check_achievements(telegram_id)
    
    def get_public_stats(self, telegram_id: int) -> Dict:
        """Get public-facing statistics"""
        profile = self.get_profile(telegram_id)
        privacy = profile['privacy']
        stats = profile['stats']
        
        public_stats = {
            'username': profile.get('username', 'Anonymous'),
            'display_name': profile.get('display_name'),
            'joined_date': profile['joined_date'],
            'badges': profile['badges']
        }
        
        # Add stats based on privacy settings
        if privacy.get('show_trades', True):
            public_stats['total_trades'] = stats['total_trades']
        
        if privacy.get('show_win_rate', True):
            public_stats['win_rate'] = stats['win_rate']
            public_stats['winning_trades'] = stats['winning_trades']
            public_stats['losing_trades'] = stats['losing_trades']
        
        if privacy.get('show_pnl', False):
            public_stats['total_pnl'] = stats['total_pnl']
            public_stats['total_pips'] = stats['total_pips']
        
        return public_stats
    
    # ============================================================================
    # BADGES & ACHIEVEMENTS
    # ============================================================================
    
    def add_badge(self, telegram_id: int, badge: str):
        """Add a badge to user profile"""
        profile = self.get_profile(telegram_id)
        if badge not in profile['badges']:
            profile['badges'].append(badge)
            self.save_data()
    
    def _check_achievements(self, telegram_id: int):
        """Check and award achievements"""
        profile = self.get_profile(telegram_id)
        stats = profile['stats']
        achievements = profile['achievements']
        
        # Define achievements
        achievement_criteria = {
            'first_trade': {'condition': stats['total_trades'] >= 1, 'badge': '🎯 First Trade'},
            'trader_10': {'condition': stats['total_trades'] >= 10, 'badge': '📊 10 Trades'},
            'trader_50': {'condition': stats['total_trades'] >= 50, 'badge': '📈 50 Trades'},
            'trader_100': {'condition': stats['total_trades'] >= 100, 'badge': '🏆 100 Trades'},
            'profitable': {'condition': stats['win_rate'] >= 60, 'badge': '💰 Profitable Trader'},
            'master': {'condition': stats['win_rate'] >= 70 and stats['total_trades'] >= 20, 'badge': '👑 Master Trader'},
            'streak_5': {'condition': abs(stats['current_streak']) >= 5, 'badge': '🔥 5-Trade Streak'},
            'streak_10': {'condition': abs(stats['current_streak']) >= 10, 'badge': '⚡ 10-Trade Streak'},
        }
        
        # Check and award new achievements
        for achievement_id, criteria in achievement_criteria.items():
            if criteria['condition'] and achievement_id not in achievements:
                achievements.append(achievement_id)
                self.add_badge(telegram_id, criteria['badge'])
    
    # ============================================================================
    # SOCIAL FEATURES
    # ============================================================================
    
    def follow_user(self, follower_id: int, target_id: int) -> bool:
        """Follow another user
        
        Returns:
            True if successful, False if not allowed
        """
        if follower_id == target_id:
            return False
        
        target_profile = self.get_profile(target_id)
        follower_profile = self.get_profile(follower_id)
        
        # Check if target allows followers
        if not target_profile['privacy'].get('allow_followers', True):
            return False
        
        # Check if already following
        if target_id in follower_profile['following']:
            return False
        
        # Check if blocked
        if follower_id in target_profile.get('blocked_users', []):
            return False
        
        # Add to following/followers lists
        follower_profile['following'].append(target_id)
        target_profile['followers'].append(follower_id)
        
        self.save_data()
        return True
    
    def unfollow_user(self, follower_id: int, target_id: int) -> bool:
        """Unfollow a user"""
        target_profile = self.get_profile(target_id)
        follower_profile = self.get_profile(follower_id)
        
        try:
            follower_profile['following'].remove(target_id)
            target_profile['followers'].remove(follower_id)
            self.save_data()
            return True
        except ValueError:
            return False
    
    def block_user(self, blocker_id: int, blocked_id: int):
        """Block a user"""
        blocker_profile = self.get_profile(blocker_id)
        
        if blocked_id not in blocker_profile['blocked_users']:
            blocker_profile['blocked_users'].append(blocked_id)
            
            # Remove from followers/following
            self.unfollow_user(blocker_id, blocked_id)
            self.unfollow_user(blocked_id, blocker_id)
            
            self.save_data()
    
    def unblock_user(self, blocker_id: int, blocked_id: int):
        """Unblock a user"""
        blocker_profile = self.get_profile(blocker_id)
        
        try:
            blocker_profile['blocked_users'].remove(blocked_id)
            self.save_data()
            return True
        except ValueError:
            return False
    
    def get_followers(self, telegram_id: int) -> List[int]:
        """Get list of followers"""
        profile = self.get_profile(telegram_id)
        return profile.get('followers', [])
    
    def get_following(self, telegram_id: int) -> List[int]:
        """Get list of users being followed"""
        profile = self.get_profile(telegram_id)
        return profile.get('following', [])
    
    # ============================================================================
    # PROFILE DISPLAY
    # ============================================================================
    
    def generate_profile_message(self, telegram_id: int, viewer_id: int = None) -> str:
        """Generate formatted profile message
        
        Args:
            telegram_id: Profile owner ID
            viewer_id: ID of user viewing the profile (for privacy checks)
        """
        if viewer_id and not self.can_view_profile(viewer_id, telegram_id):
            return "🔒 This profile is private."
        
        profile = self.get_profile(telegram_id)
        stats = profile['stats']
        privacy = profile['privacy']
        
        is_own_profile = (viewer_id == telegram_id)
        
        msg = "👤 **USER PROFILE**\n\n"
        
        # Basic info
        display_name = profile.get('display_name') or profile.get('username') or "Anonymous"
        msg += f"*Name:* {display_name}\n"
        
        # Badges
        if profile['badges']:
            msg += f"*Badges:* {' '.join(profile['badges'])}\n"
        
        msg += f"*Member Since:* {profile['joined_date']}\n\n"
        
        # Bio
        if profile.get('bio'):
            msg += f"*Bio:* {profile['bio']}\n\n"
        
        # Trading stats
        msg += "📊 **TRADING STATS**\n\n"
        
        if privacy['show_trades'] or is_own_profile:
            msg += f"Total Trades: {stats['total_trades']}\n"
        
        if privacy['show_win_rate'] or is_own_profile:
            msg += f"Win Rate: {stats['win_rate']}%\n"
            msg += f"Wins: {stats['winning_trades']} | Losses: {stats['losing_trades']}\n"
        
        if privacy['show_pnl'] or is_own_profile:
            msg += f"Total Pips: +{stats['total_pips']:.1f}\n"
            msg += f"Total P&L: ${stats['total_pnl']:.2f}\n"
        
        if stats['current_streak'] != 0:
            streak_emoji = "🔥" if stats['current_streak'] > 0 else "❄️"
            msg += f"{streak_emoji} Current Streak: {abs(stats['current_streak'])} {'wins' if stats['current_streak'] > 0 else 'losses'}\n"
        
        msg += "\n"
        
        # Social stats
        msg += "👥 **SOCIAL**\n\n"
        msg += f"Followers: {len(profile.get('followers', []))}\n"
        msg += f"Following: {len(profile.get('following', []))}\n"
        
        if is_own_profile:
            msg += "\n💡 *Commands:*\n"
            msg += "`/profile edit` - Edit profile\n"
            msg += "`/profile privacy` - Privacy settings\n"
        
        return msg


if __name__ == "__main__":
    # Test profile manager
    pm = UserProfileManager()
    
    # Create test profile
    profile = pm.get_profile(123456789)
    print(f"Profile created: {profile['telegram_id']}")
    
    # Simulate trades
    pm.update_trade_stats(123456789, {'won': True, 'pips': 25, 'pnl': 50})
    pm.update_trade_stats(123456789, {'won': True, 'pips': 30, 'pnl': 60})
    pm.update_trade_stats(123456789, {'won': False, 'pips': -15, 'pnl': -30})
    
    # View profile
    print("\nProfile Message:")
    print(pm.generate_profile_message(123456789, 123456789))


















