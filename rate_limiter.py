"""
Rate Limiting Module for UR Trading Expert Bot
Implements per-user rate limiting to prevent abuse
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter with per-user tracking"""
    
    def __init__(self):
        # Store request timestamps per user
        # Format: {user_id: [timestamp1, timestamp2, ...]}
        self.user_requests: Dict[int, list] = defaultdict(list)
        
        # Rate limit configuration
        self.requests_per_minute = 100  # 100 requests per minute per user
        self.requests_per_hour = 1000   # 1000 requests per hour per user
        self.burst_limit = 20           # Max 20 requests in 10 seconds
        
        # Cleanup old entries periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # Clean up every hour
    
    def _cleanup_old_entries(self):
        """Remove old request timestamps to prevent memory bloat"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 3600  # Keep only last hour
        for user_id in list(self.user_requests.keys()):
            self.user_requests[user_id] = [
                ts for ts in self.user_requests[user_id] 
                if ts > cutoff_time
            ]
            # Remove empty entries
            if not self.user_requests[user_id]:
                del self.user_requests[user_id]
        
        self.last_cleanup = current_time
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits
        
        Returns:
            (allowed: bool, message: str)
        """
        current_time = time.time()
        
        # Cleanup old entries periodically
        self._cleanup_old_entries()
        
        # Get user's request history
        user_history = self.user_requests[user_id]
        
        # Remove requests older than 1 hour
        one_hour_ago = current_time - 3600
        user_history = [ts for ts in user_history if ts > one_hour_ago]
        self.user_requests[user_id] = user_history
        
        # Check burst limit (last 10 seconds)
        ten_seconds_ago = current_time - 10
        recent_requests = [ts for ts in user_history if ts > ten_seconds_ago]
        if len(recent_requests) >= self.burst_limit:
            wait_time = int(10 - (current_time - recent_requests[0]))
            return False, f"⏳ Too many requests. Please wait {wait_time} seconds."
        
        # Check per-minute limit
        one_minute_ago = current_time - 60
        minute_requests = [ts for ts in user_history if ts > one_minute_ago]
        if len(minute_requests) >= self.requests_per_minute:
            wait_time = int(60 - (current_time - minute_requests[0]))
            return False, f"⏳ Rate limit exceeded. Please wait {wait_time} seconds."
        
        # Check per-hour limit
        if len(user_history) >= self.requests_per_hour:
            wait_time = int(3600 - (current_time - user_history[0]))
            minutes = wait_time // 60
            return False, f"⏳ Hourly limit exceeded. Please wait {minutes} minutes."
        
        # All checks passed - record this request
        user_history.append(current_time)
        self.user_requests[user_id] = user_history
        
        return True, "OK"
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get rate limit statistics for a user"""
        current_time = time.time()
        user_history = self.user_requests[user_id]
        
        # Remove old entries
        one_hour_ago = current_time - 3600
        user_history = [ts for ts in user_history if ts > one_hour_ago]
        
        return {
            'requests_last_minute': len([ts for ts in user_history if ts > current_time - 60]),
            'requests_last_hour': len(user_history),
            'limit_per_minute': self.requests_per_minute,
            'limit_per_hour': self.requests_per_hour,
            'burst_limit': self.burst_limit
        }
    
    def reset_user_limit(self, user_id: int):
        """Reset rate limit for a user (admin function)"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
        logger.info(f"Rate limit reset for user {user_id}")


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_decorator(func):
    """Decorator to add rate limiting to bot commands"""
    @wraps(func)
    async def wrapper(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_id = update.effective_user.id
        
        # Check rate limit
        allowed, message = rate_limiter.check_rate_limit(user_id)
        
        if not allowed:
            await update.message.reply_text(message)
            return
        
        # Call original function
        return await func(update, context)
    
    return wrapper


def check_rate_limit(user_id: int) -> Tuple[bool, str]:
    """Check rate limit for a user (for use in handlers)"""
    return rate_limiter.check_rate_limit(user_id)


def get_rate_limit_stats(user_id: int) -> Dict:
    """Get rate limit statistics for a user"""
    return rate_limiter.get_user_stats(user_id)



