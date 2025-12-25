"""
Community Features Module
Handles signal ratings, copy trading, polls, and community engagement
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CommunityManager:
    """Manages community features like signal ratings, polls, and copy trading"""
    
    def __init__(self, data_file="community_data.json"):
        self.data_file = data_file
        self.data = {
            'signal_ratings': {},  # {signal_id: [{user_id, rating, comment, timestamp}]}
            'polls': [],
            'success_stories': [],
            'copy_trading': {}  # {follower_id: {leader_id, settings}}
        }
        self.load_data()
    
    def load_data(self):
        """Load community data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save community data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    # ============================================================================
    # SIGNAL RATING SYSTEM
    # ============================================================================
    
    def rate_signal(self, signal_id: int, user_id: int, rating: int, comment: str = None) -> bool:
        """Rate a signal (1-5 stars)
        
        Args:
            signal_id: Signal ID to rate
            user_id: User rating the signal
            rating: 1-5 stars
            comment: Optional comment
        
        Returns:
            True if successful
        """
        if not 1 <= rating <= 5:
            return False
        
        signal_id_str = str(signal_id)
        
        if signal_id_str not in self.data['signal_ratings']:
            self.data['signal_ratings'][signal_id_str] = []
        
        # Check if user already rated this signal
        ratings = self.data['signal_ratings'][signal_id_str]
        for r in ratings:
            if r['user_id'] == user_id:
                # Update existing rating
                r['rating'] = rating
                r['comment'] = comment
                r['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_data()
                return True
        
        # Add new rating
        ratings.append({
            'user_id': user_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        self.save_data()
        return True
    
    def get_signal_rating(self, signal_id: int) -> Dict:
        """Get average rating and all ratings for a signal"""
        signal_id_str = str(signal_id)
        ratings = self.data['signal_ratings'].get(signal_id_str, [])
        
        if not ratings:
            return {
                'average': 0,
                'count': 0,
                'ratings': []
            }
        
        total = sum(r['rating'] for r in ratings)
        average = total / len(ratings)
        
        return {
            'average': round(average, 1),
            'count': len(ratings),
            'ratings': ratings
        }
    
    def get_signal_rating_message(self, signal_id: int) -> str:
        """Get formatted signal rating message"""
        rating_data = self.get_signal_rating(signal_id)
        
        if rating_data['count'] == 0:
            return f"⭐ *Signal #{signal_id}*\n\nNo ratings yet. Be the first to rate!\nUse: `/rate {signal_id} [1-5]`"
        
        avg = rating_data['average']
        count = rating_data['count']
        stars = '⭐' * int(round(avg))
        
        msg = f"⭐ *Signal #{signal_id} Rating*\n\n"
        msg += f"Average: *{avg}/5.0* {stars}\n"
        msg += f"Total Ratings: {count}\n\n"
        
        # Show recent comments
        recent_comments = [r for r in rating_data['ratings'] if r.get('comment')][-3:]
        
        if recent_comments:
            msg += "*Recent Comments:*\n"
            for r in reversed(recent_comments):
                comment = r['comment'][:100]  # Limit length
                msg += f"• {comment} ({r['rating']}⭐)\n"
        
        return msg
    
    # ============================================================================
    # COPY TRADING
    # ============================================================================
    
    def enable_copy_trading(self, follower_id: int, leader_id: int, settings: Dict) -> bool:
        """Enable copy trading for a user
        
        Args:
            follower_id: User who wants to copy
            leader_id: User to copy
            settings: Dict with copy settings (lot_multiplier, max_risk, etc.)
        
        Returns:
            True if successful
        """
        follower_id_str = str(follower_id)
        
        if follower_id == leader_id:
            return False
        
        if follower_id_str not in self.data['copy_trading']:
            self.data['copy_trading'][follower_id_str] = []
        
        # Check if already copying this user
        for copy_config in self.data['copy_trading'][follower_id_str]:
            if copy_config['leader_id'] == leader_id:
                return False
        
        # Add copy configuration
        self.data['copy_trading'][follower_id_str].append({
            'leader_id': leader_id,
            'enabled': True,
            'lot_multiplier': settings.get('lot_multiplier', 1.0),
            'max_risk_per_trade': settings.get('max_risk', 2.0),
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        self.save_data()
        return True
    
    def disable_copy_trading(self, follower_id: int, leader_id: int) -> bool:
        """Disable copy trading"""
        follower_id_str = str(follower_id)
        
        if follower_id_str not in self.data['copy_trading']:
            return False
        
        configs = self.data['copy_trading'][follower_id_str]
        for i, config in enumerate(configs):
            if config['leader_id'] == leader_id:
                del configs[i]
                self.save_data()
                return True
        
        return False
    
    def get_copy_trading_followers(self, leader_id: int) -> List[int]:
        """Get list of users copying this trader"""
        followers = []
        for follower_id_str, configs in self.data['copy_trading'].items():
            for config in configs:
                if config['leader_id'] == leader_id and config['enabled']:
                    followers.append(int(follower_id_str))
        return followers
    
    # ============================================================================
    # COMMUNITY POLLS
    # ============================================================================
    
    def create_poll(self, question: str, options: List[str], creator_id: int) -> int:
        """Create a community poll
        
        Returns:
            poll_id
        """
        poll_id = len(self.data['polls']) + 1
        
        poll = {
            'id': poll_id,
            'question': question,
            'options': {opt: 0 for opt in options},
            'votes': {},  # {user_id: option_chosen}
            'creator_id': creator_id,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        }
        
        self.data['polls'].append(poll)
        self.save_data()
        return poll_id
    
    def vote_in_poll(self, poll_id: int, user_id: int, option: str) -> bool:
        """Vote in a poll"""
        for poll in self.data['polls']:
            if poll['id'] == poll_id and poll['active']:
                if option in poll['options']:
                    # Remove previous vote if exists
                    if user_id in poll['votes']:
                        old_option = poll['votes'][user_id]
                        poll['options'][old_option] -= 1
                    
                    # Add new vote
                    poll['votes'][user_id] = option
                    poll['options'][option] += 1
                    self.save_data()
                    return True
        
        return False
    
    def get_poll_results(self, poll_id: int) -> Optional[Dict]:
        """Get poll results"""
        for poll in self.data['polls']:
            if poll['id'] == poll_id:
                total_votes = sum(poll['options'].values())
                
                return {
                    'id': poll_id,
                    'question': poll['question'],
                    'options': poll['options'],
                    'total_votes': total_votes,
                    'active': poll['active']
                }
        
        return None
    
    def format_poll_message(self, poll_id: int) -> str:
        """Format poll results message"""
        results = self.get_poll_results(poll_id)
        
        if not results:
            return "❌ Poll not found"
        
        total = results['total_votes']
        
        msg = f"📊 **COMMUNITY POLL #{poll_id}**\n\n"
        msg += f"*{results['question']}*\n\n"
        
        msg += "*Results:*\n"
        for option, votes in sorted(results['options'].items(), key=lambda x: x[1], reverse=True):
            pct = (votes / total * 100) if total > 0 else 0
            bar = '█' * int(pct / 10)
            msg += f"{option}: {votes} votes ({pct:.0f}%)\n{bar}\n\n"
        
        msg += f"Total Votes: {total}\n\n"
        
        if results['active']:
            msg += f"Vote with: `/poll {poll_id} vote [option]`"
        else:
            msg += "🔒 Poll closed"
        
        return msg
    
    # ============================================================================
    # SUCCESS STORIES
    # ============================================================================
    
    def add_success_story(self, user_id: int, story: str, profit: float, timeframe: str):
        """Add a success story"""
        story_data = {
            'user_id': user_id,
            'story': story,
            'profit': profit,
            'timeframe': timeframe,
            'submitted_at': datetime.now().strftime('%Y-%m-%d'),
            'approved': False  # Admin needs to approve
        }
        
        self.data['success_stories'].append(story_data)
        self.save_data()
    
    def get_success_stories(self, approved_only: bool = True) -> List[Dict]:
        """Get success stories"""
        stories = self.data['success_stories']
        
        if approved_only:
            stories = [s for s in stories if s.get('approved', False)]
        
        return sorted(stories, key=lambda x: x['profit'], reverse=True)
    
    def format_success_stories_message(self) -> str:
        """Format success stories message"""
        stories = self.get_success_stories(approved_only=True)
        
        if not stories:
            msg = "🌟 **SUCCESS STORIES**\n\n"
            msg += "No success stories yet. Be the first!\n\n"
            msg += "Submit yours with:\n"
            msg += "`/success submit [profit] [timeframe] [story]`"
            return msg
        
        msg = "🌟 **TRADING SUCCESS STORIES**\n\n"
        
        for i, story in enumerate(stories[:5], 1):
            msg += f"*#{i} - {story['timeframe']} | +${story['profit']:.0f}*\n"
            msg += f"{story['story'][:150]}\n\n"
        
        msg += "💡 Submit your success:\n"
        msg += "`/success submit [profit] [timeframe] [story]`"
        
        return msg


if __name__ == "__main__":
    # Test community manager
    cm = CommunityManager()
    
    # Test signal rating
    cm.rate_signal(1, 123, 5, "Great signal!")
    cm.rate_signal(1, 456, 4, "Good setup")
    cm.rate_signal(1, 789, 5, "Perfect entry!")
    
    print(cm.get_signal_rating_message(1))
    print()
    
    # Test poll
    poll_id = cm.create_poll("Which asset should we add next?", ["EUR/GBP", "GBP/JPY", "XAU/USD"], 123)
    cm.vote_in_poll(poll_id, 123, "EUR/GBP")
    cm.vote_in_poll(poll_id, 456, "EUR/GBP")
    cm.vote_in_poll(poll_id, 789, "GBP/JPY")
    
    print(cm.format_poll_message(poll_id))


















