"""
Forex Session Manager
Manages trading sessions and liquidity for forex pairs
London, New York, Tokyo sessions with overlap detection
"""

from datetime import datetime, time
import pytz


class ForexSessionManager:
    """Manage forex trading sessions and liquidity"""
    
    def __init__(self):
        """Initialize session times (in UTC)"""
        self.sessions = {
            'tokyo': {
                'start': time(0, 0),
                'end': time(9, 0),
                'name': 'Tokyo',
                'liquidity_score': 60
            },
            'london': {
                'start': time(8, 0),
                'end': time(16, 0),
                'name': 'London',
                'liquidity_score': 90
            },
            'new_york': {
                'start': time(13, 0),
                'end': time(21, 0),
                'name': 'New York',
                'liquidity_score': 85
            }
        }
        
        # Overlap periods (highest liquidity)
        self.overlaps = {
            'london_ny': {
                'start': time(13, 0),
                'end': time(16, 0),
                'name': 'London/NY Overlap',
                'liquidity_score': 100
            },
            'tokyo_london': {
                'start': time(8, 0),
                'end': time(9, 0),
                'name': 'Tokyo/London Overlap',
                'liquidity_score': 75
            }
        }
    
    def get_current_session(self, utc_time=None):
        """
        Get current trading session
        
        Args:
            utc_time: datetime object in UTC (default: now)
        
        Returns:
            dict: Session information
        """
        if utc_time is None:
            utc_time = datetime.now(pytz.UTC)
        
        current_time = utc_time.time()
        
        active_sessions = []
        
        # Check each session
        for session_key, session in self.sessions.items():
            if self._is_time_in_range(current_time, session['start'], session['end']):
                active_sessions.append(session['name'])
        
        # Check for overlaps
        overlap = None
        for overlap_key, overlap_info in self.overlaps.items():
            if self._is_time_in_range(current_time, overlap_info['start'], overlap_info['end']):
                overlap = overlap_info['name']
                break
        
        # Calculate liquidity score
        if overlap:
            liquidity_score = self.overlaps[list(self.overlaps.keys())[0]]['liquidity_score'] if overlap == 'London/NY Overlap' else 75
        elif active_sessions:
            liquidity_score = max([self.sessions[k]['liquidity_score'] for k, v in self.sessions.items() if v['name'] in active_sessions])
        else:
            liquidity_score = 20  # Off-hours
        
        return {
            'current_time_utc': utc_time.strftime('%H:%M UTC'),
            'active_sessions': active_sessions,
            'overlap': overlap,
            'liquidity_score': liquidity_score,
            'is_optimal': liquidity_score >= 90,
            'is_acceptable': liquidity_score >= 70
        }
    
    def is_optimal_trading_time(self, utc_time=None):
        """
        Check if current time is optimal for trading
        
        Returns:
            bool: True if London/NY overlap (13-16 UTC)
        """
        session = self.get_current_session(utc_time)
        return session['is_optimal']
    
    def is_acceptable_trading_time(self, utc_time=None):
        """
        Check if current time is acceptable for trading
        
        Returns:
            bool: True if liquidity >= 70
        """
        session = self.get_current_session(utc_time)
        return session['is_acceptable']
    
    def get_next_optimal_time(self, utc_time=None):
        """
        Get next optimal trading time (London/NY overlap)
        
        Returns:
            str: Time until next optimal period
        """
        if utc_time is None:
            utc_time = datetime.now(pytz.UTC)
        
        current_hour = utc_time.hour
        
        # London/NY overlap is 13-16 UTC
        if current_hour < 13:
            hours_until = 13 - current_hour
            return f"{hours_until} hours until London/NY overlap"
        elif current_hour < 16:
            return "Currently in London/NY overlap (optimal time)"
        else:
            hours_until = (24 - current_hour) + 13
            return f"{hours_until} hours until next London/NY overlap"
    
    def get_session_analysis(self, pair, utc_time=None):
        """
        Get complete session analysis for a forex pair
        
        Args:
            pair: Forex pair (e.g., "EURUSD")
        
        Returns:
            dict: Complete session analysis
        """
        session = self.get_current_session(utc_time)
        
        # Pair-specific recommendations
        pair_sessions = {
            'EURUSD': ['London', 'New York', 'London/NY Overlap'],
            'GBPUSD': ['London', 'New York', 'London/NY Overlap'],
            'USDJPY': ['Tokyo', 'New York'],
            'EURJPY': ['Tokyo', 'London'],  # Already there!
            'AUDUSD': ['Tokyo', 'London'],
            'USDCAD': ['London', 'New York', 'London/NY Overlap'],
        }
        
        recommended_sessions = pair_sessions.get(pair, ['London', 'New York'])
        
        # Check if current session is recommended for this pair
        is_recommended = any(s in session['active_sessions'] for s in recommended_sessions) or \
                        (session['overlap'] and session['overlap'] in recommended_sessions)
        
        return {
            'pair': pair,
            'session_info': session,
            'recommended_sessions': recommended_sessions,
            'is_recommended_time': is_recommended,
            'next_optimal': self.get_next_optimal_time(utc_time),
            'trading_advice': self._get_trading_advice(session, is_recommended)
        }
    
    def _is_time_in_range(self, current, start, end):
        """Check if current time is within range"""
        if start <= end:
            return start <= current <= end
        else:  # Crosses midnight
            return current >= start or current <= end
    
    def _get_trading_advice(self, session, is_recommended):
        """Get trading advice based on session"""
        if session['is_optimal']:
            return "EXCELLENT - Peak liquidity, optimal for trading"
        elif session['is_acceptable']:
            if is_recommended:
                return "GOOD - Acceptable liquidity for this pair"
            else:
                return "CAUTION - Not optimal session for this pair"
        else:
            return "AVOID - Low liquidity, wait for better session"


# Testing
if __name__ == "__main__":
    print("Testing Forex Session Manager...")
    print("="*60)
    
    manager = ForexSessionManager()
    
    # Test current session
    print("\n1. Current Session:")
    session = manager.get_current_session()
    print(f"   Time: {session['current_time_utc']}")
    print(f"   Active Sessions: {session['active_sessions']}")
    print(f"   Overlap: {session['overlap']}")
    print(f"   Liquidity Score: {session['liquidity_score']}/100")
    print(f"   Is Optimal: {session['is_optimal']}")
    print(f"   Is Acceptable: {session['is_acceptable']}")
    
    # Test optimal time check
    print("\n2. Optimal Trading Time:")
    print(f"   {manager.get_next_optimal_time()}")
    
    # Test pair-specific analysis
    print("\n3. EUR/USD Session Analysis:")
    analysis = manager.get_session_analysis("EURUSD")
    print(f"   Recommended Sessions: {analysis['recommended_sessions']}")
    print(f"   Is Recommended Time: {analysis['is_recommended_time']}")
    print(f"   Advice: {analysis['trading_advice']}")
    
    # Test different times
    print("\n4. Testing Different Times:")
    test_times = [
        datetime(2025, 12, 3, 5, 0, tzinfo=pytz.UTC),   # Tokyo
        datetime(2025, 12, 3, 10, 0, tzinfo=pytz.UTC),  # London
        datetime(2025, 12, 3, 14, 0, tzinfo=pytz.UTC),  # London/NY overlap
        datetime(2025, 12, 3, 18, 0, tzinfo=pytz.UTC),  # NY
        datetime(2025, 12, 3, 23, 0, tzinfo=pytz.UTC),  # Off-hours
    ]
    
    for test_time in test_times:
        session = manager.get_current_session(test_time)
        print(f"   {test_time.strftime('%H:%M UTC')}: {session['active_sessions']} - Liquidity: {session['liquidity_score']}")
    
    print("\n" + "="*60)
    print("[OK] Session Manager working!")
