"""
Leaderboard Module
Manages leaderboards for win rate, profit, activity, and streaks
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LeaderboardManager:
    """Manages various leaderboards for trader rankings"""
    
    def __init__(self, profile_manager):
        """Initialize with profile manager for data access"""
        self.profile_manager = profile_manager
    
    # ============================================================================
    # LEADERBOARD GENERATION
    # ============================================================================
    
    def get_leaderboard(self, category: str, period: str = 'all', limit: int = 10) -> List[Dict]:
        """Get leaderboard for specified category
        
        Args:
            category: 'winrate', 'profit', 'active', 'streak'
            period: 'all', 'monthly', 'weekly'
            limit: Number of users to return
        
        Returns:
            List of dicts with user rankings
        """
        # Get all profiles
        profiles = self.profile_manager.profiles
        
        # Filter based on privacy settings
        eligible_users = []
        for user_id_str, profile in profiles.items():
            # Check if user opted into leaderboard
            if not profile['privacy'].get('show_in_leaderboard', True):
                continue
            
            # Check minimum trades requirement (prevents gaming)
            if profile['stats']['total_trades'] < 20:
                continue
            
            eligible_users.append(profile)
        
        # Sort based on category
        if category == 'winrate':
            sorted_users = sorted(eligible_users, key=lambda x: (x['stats']['win_rate'], x['stats']['total_trades']), reverse=True)
        elif category == 'profit':
            sorted_users = sorted(eligible_users, key=lambda x: x['stats']['total_pips'], reverse=True)
        elif category == 'active':
            sorted_users = sorted(eligible_users, key=lambda x: x['stats']['total_trades'], reverse=True)
        elif category == 'streak':
            sorted_users = sorted(eligible_users, key=lambda x: abs(x['stats']['best_streak']), reverse=True)
        else:
            return []
        
        # Build leaderboard
        leaderboard = []
        for rank, profile in enumerate(sorted_users[:limit], 1):
            entry = {
                'rank': rank,
                'user_id': profile['telegram_id'],
                'display_name': profile.get('display_name') or profile.get('username') or 'Anonymous',
                'badges': profile.get('badges', []),
                'stats': {}
            }
            
            # Add category-specific stats
            if category == 'winrate':
                entry['stats'] = {
                    'win_rate': profile['stats']['win_rate'],
                    'total_trades': profile['stats']['total_trades'],
                    'wins': profile['stats']['winning_trades']
                }
            elif category == 'profit':
                entry['stats'] = {
                    'total_pips': profile['stats']['total_pips'],
                    'win_rate': profile['stats']['win_rate'],
                    'total_trades': profile['stats']['total_trades']
                }
            elif category == 'active':
                entry['stats'] = {
                    'total_trades': profile['stats']['total_trades'],
                    'win_rate': profile['stats']['win_rate'],
                    'trades_this_month': profile['stats'].get('trades_this_month', 0)
                }
            elif category == 'streak':
                entry['stats'] = {
                    'best_streak': profile['stats']['best_streak'],
                    'current_streak': profile['stats']['current_streak'],
                    'win_rate': profile['stats']['win_rate']
                }
            
            leaderboard.append(entry)
        
        return leaderboard
    
    # ============================================================================
    # LEADERBOARD FORMATTING
    # ============================================================================
    
    def format_leaderboard_message(self, category: str, period: str = 'all', limit: int = 10) -> str:
        """Generate formatted leaderboard message
        
        Args:
            category: 'winrate', 'profit', 'active', 'streak'
            period: 'all', 'monthly', 'weekly'
            limit: Number of users to show
        """
        leaderboard = self.get_leaderboard(category, period, limit)
        
        if not leaderboard:
            return "📊 No users currently eligible for leaderboard.\n\n💡 *Requirement:* Minimum 20 trades"
        
        # Category titles
        titles = {
            'winrate': '🏆 WIN RATE LEADERBOARD',
            'profit': '💰 PROFIT LEADERBOARD',
            'active': '📈 MOST ACTIVE TRADERS',
            'streak': '🔥 BEST STREAKS'
        }
        
        msg = f"{titles.get(category, 'LEADERBOARD')}\n\n"
        
        # Add period info
        period_text = {
            'all': 'All Time',
            'monthly': 'This Month',
            'weekly': 'This Week'
        }
        msg += f"*Period:* {period_text.get(period, 'All Time')}\n"
        msg += f"*Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Add leaderboard entries
        for entry in leaderboard:
            rank_emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(entry['rank'], f"{entry['rank']}.")
            
            name = entry['display_name']
            badges = ' '.join(entry['badges'][:2]) if entry['badges'] else ''
            
            msg += f"{rank_emoji} *{name}* {badges}\n"
            
            # Category-specific stats
            if category == 'winrate':
                msg += f"   Win Rate: *{entry['stats']['win_rate']}%* ({entry['stats']['wins']}/{entry['stats']['total_trades']})\n"
            elif category == 'profit':
                msg += f"   Pips: *+{entry['stats']['total_pips']:.1f}* | WR: {entry['stats']['win_rate']}%\n"
            elif category == 'active':
                msg += f"   Trades: *{entry['stats']['total_trades']}* | WR: {entry['stats']['win_rate']}%\n"
            elif category == 'streak':
                streak_type = 'wins' if entry['stats']['best_streak'] > 0 else 'losses'
                current_status = ""
                if abs(entry['stats']['current_streak']) >= 3:
                    current_status = f" | Current: {abs(entry['stats']['current_streak'])}"
                msg += f"   Best: *{abs(entry['stats']['best_streak'])} {streak_type}*{current_status}\n"
            
            msg += "\n"
        
        # Add footer
        msg += "─" * 35 + "\n\n"
        msg += "💡 *Requirements:*\n"
        msg += "• Minimum 20 trades\n"
        msg += "• Opt-in via `/profile privacy show_in_leaderboard on`\n\n"
        msg += "*Commands:*\n"
        msg += "`/leaderboard winrate` - Top win rates\n"
        msg += "`/leaderboard profit` - Most profitable\n"
        msg += "`/leaderboard active` - Most active\n"
        msg += "`/leaderboard streak` - Best streaks"
        
        return msg
    
    # ============================================================================
    # USER RANKING
    # ============================================================================
    
    def get_user_rank(self, telegram_id: int, category: str) -> Optional[int]:
        """Get user's rank in a specific leaderboard
        
        Returns:
            Rank (1-indexed) or None if not ranked
        """
        leaderboard = self.get_leaderboard(category, 'all', limit=1000)
        
        for entry in leaderboard:
            if entry['user_id'] == telegram_id:
                return entry['rank']
        
        return None
    
    def get_user_ranking_message(self, telegram_id: int) -> str:
        """Get user's rankings across all categories"""
        profile = self.profile_manager.get_profile(telegram_id)
        stats = profile['stats']
        
        msg = "📊 **YOUR RANKINGS**\n\n"
        
        # Check eligibility
        if stats['total_trades'] < 20:
            msg += f"⚠️ You need {20 - stats['total_trades']} more trades to qualify for leaderboards.\n\n"
            msg += f"*Current Progress:*\n"
            msg += f"Trades: {stats['total_trades']}/20\n"
            msg += f"Win Rate: {stats['win_rate']}%\n\n"
            msg += "Keep trading to unlock leaderboard rankings! 🚀"
            return msg
        
        # Check opt-in
        if not profile['privacy'].get('show_in_leaderboard', True):
            msg += "🔒 You've opted out of leaderboards.\n\n"
            msg += "To participate:\n"
            msg += "`/profile privacy show_in_leaderboard on`"
            return msg
        
        # Get rankings
        winrate_rank = self.get_user_rank(telegram_id, 'winrate')
        profit_rank = self.get_user_rank(telegram_id, 'profit')
        active_rank = self.get_user_rank(telegram_id, 'active')
        streak_rank = self.get_user_rank(telegram_id, 'streak')
        
        msg += f"*Win Rate:* #{winrate_rank or 'Unranked'}\n"
        msg += f"*Profit:* #{profit_rank or 'Unranked'}\n"
        msg += f"*Activity:* #{active_rank or 'Unranked'}\n"
        msg += f"*Streak:* #{streak_rank or 'Unranked'}\n\n"
        
        msg += f"*Your Stats:*\n"
        msg += f"Win Rate: {stats['win_rate']}%\n"
        msg += f"Total Pips: +{stats['total_pips']:.1f}\n"
        msg += f"Total Trades: {stats['total_trades']}\n"
        msg += f"Best Streak: {abs(stats['best_streak'])}\n\n"
        
        msg += "Use `/leaderboard [category]` to see full rankings!"
        
        return msg


if __name__ == "__main__":
    # Test leaderboard
    from user_profiles import UserProfileManager
    
    pm = UserProfileManager()
    lm = LeaderboardManager(pm)
    
    # Create test users
    for i in range(5):
        user_id = 100 + i
        pm.get_profile(user_id)
        pm.update_profile(user_id, display_name=f"Trader {i+1}")
        
        # Simulate trades
        for _ in range(25):
            won = (i * 20 + _) % 3 != 0  # Varying win rates
            pm.update_trade_stats(user_id, {
                'won': won,
                'pips': 20 if won else -10,
                'pnl': 40 if won else -20
            })
    
    # View leaderboard
    print(lm.format_leaderboard_message('winrate'))


















