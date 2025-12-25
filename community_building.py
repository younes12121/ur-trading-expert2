"""
Community Building Module for UR Trading Expert Bot
Manages Discord, Telegram groups, TradingView, and webinars
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CommunityManager:
    """Manages global community building initiatives"""
    
    def __init__(self):
        self.community_data_file = "community_data.json"
        self.community_data = self._load_community_data()
    
    def _load_community_data(self) -> Dict:
        """Load community data from file"""
        try:
            with open(self.community_data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "discord": {
                    "server_id": None,
                    "members": 0,
                    "channels": [],
                    "languages": ["en", "es", "ar", "zh", "ru", "pt", "ja", "de", "fr", "hi"]
                },
                "telegram_groups": {
                    "global": {"members": 0, "link": None},
                    "premium": {"members": 0, "link": None},
                    "vip": {"members": 0, "link": None},
                    "regional": {}
                },
                "tradingview": {
                    "ideas_published": 0,
                    "followers": 0,
                    "profile_link": None
                },
                "youtube": {
                    "subscribers": 0,
                    "videos": 0,
                    "channel_link": None
                },
                "reddit": {
                    "subreddit": "r/URTradingExpert",
                    "members": 0,
                    "posts": 0
                },
                "webinars": {
                    "upcoming": [],
                    "past": [],
                    "schedule": {
                        "frequency": "weekly",
                        "timezones": ["US/Eastern", "Europe/London", "Asia/Tokyo"]
                    }
                },
                "leaderboards": {
                    "global": [],
                    "regional": {},
                    "categories": ["win_rate", "profit_factor", "total_trades", "consistency"]
                }
            }
    
    def _save_community_data(self):
        """Save community data to file"""
        with open(self.community_data_file, 'w') as f:
            json.dump(self.community_data, f, indent=2)
    
    def create_webinar(self, title: str, date: datetime, timezone: str, 
                      description: str, registration_link: str) -> Dict:
        """Create a new webinar"""
        webinar = {
            "id": len(self.community_data["webinars"]["upcoming"]) + 1,
            "title": title,
            "date": date.isoformat(),
            "timezone": timezone,
            "description": description,
            "registration_link": registration_link,
            "registrations": 0,
            "status": "upcoming"
        }
        
        self.community_data["webinars"]["upcoming"].append(webinar)
        self._save_community_data()
        
        logger.info(f"Created webinar: {title}")
        return webinar
    
    def get_upcoming_webinars(self, limit: int = 5) -> List[Dict]:
        """Get upcoming webinars"""
        upcoming = self.community_data["webinars"]["upcoming"]
        # Filter by date
        now = datetime.now()
        upcoming = [
            w for w in upcoming 
            if datetime.fromisoformat(w["date"]) > now
        ]
        return sorted(upcoming, key=lambda x: x["date"])[:limit]
    
    def create_trading_challenge(self, name: str, start_date: datetime, 
                                end_date: datetime, rules: Dict) -> Dict:
        """Create a trading challenge"""
        challenge = {
            "id": len(self.community_data.get("challenges", [])) + 1,
            "name": name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "rules": rules,
            "participants": 0,
            "leaderboard": [],
            "status": "upcoming"
        }
        
        if "challenges" not in self.community_data:
            self.community_data["challenges"] = []
        self.community_data["challenges"].append(challenge)
        self._save_community_data()
        
        return challenge
    
    def update_leaderboard(self, category: str, user_id: int, score: float):
        """Update leaderboard for a category"""
        if category not in self.community_data["leaderboards"]["categories"]:
            return
        
        leaderboard = self.community_data["leaderboards"].get(category, [])
        
        # Find or create entry
        entry = next((e for e in leaderboard if e["user_id"] == user_id), None)
        if entry:
            entry["score"] = score
            entry["updated_at"] = datetime.now().isoformat()
        else:
            leaderboard.append({
                "user_id": user_id,
                "score": score,
                "rank": 0,
                "updated_at": datetime.now().isoformat()
            })
        
        # Sort and rank
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        for i, entry in enumerate(leaderboard, 1):
            entry["rank"] = i
        
        self.community_data["leaderboards"][category] = leaderboard[:100]  # Top 100
        self._save_community_data()
    
    def get_leaderboard(self, category: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for a category"""
        leaderboard = self.community_data["leaderboards"].get(category, [])
        return leaderboard[:limit]
    
    def create_success_story(self, user_id: int, title: str, content: str, 
                           metrics: Dict) -> Dict:
        """Create a user success story"""
        story = {
            "id": len(self.community_data.get("success_stories", [])) + 1,
            "user_id": user_id,
            "title": title,
            "content": content,
            "metrics": metrics,
            "date": datetime.now().isoformat(),
            "featured": False
        }
        
        if "success_stories" not in self.community_data:
            self.community_data["success_stories"] = []
        self.community_data["success_stories"].append(story)
        self._save_community_data()
        
        return story
    
    def get_community_stats(self) -> Dict:
        """Get overall community statistics"""
        return {
            "total_members": (
                self.community_data["discord"]["members"] +
                self.community_data["telegram_groups"]["global"]["members"] +
                self.community_data["tradingview"]["followers"] +
                self.community_data["youtube"]["subscribers"] +
                self.community_data["reddit"]["members"]
            ),
            "discord_members": self.community_data["discord"]["members"],
            "telegram_members": self.community_data["telegram_groups"]["global"]["members"],
            "tradingview_followers": self.community_data["tradingview"]["followers"],
            "youtube_subscribers": self.community_data["youtube"]["subscribers"],
            "reddit_members": self.community_data["reddit"]["members"],
            "upcoming_webinars": len(self.community_data["webinars"]["upcoming"]),
            "total_webinars": len(self.community_data["webinars"]["past"]) + len(self.community_data["webinars"]["upcoming"]),
            "success_stories": len(self.community_data.get("success_stories", []))
        }

# Global instance
community_manager = CommunityManager()

if __name__ == "__main__":
    # Example usage
    stats = community_manager.get_community_stats()
    print("Community Statistics:")
    print(json.dumps(stats, indent=2))



