"""
Economic Calendar Module for Forex Trading
Fetches high-impact economic events to avoid trading during volatile news releases
Uses free APIs: Forex Factory, Trading Economics, or similar
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class EconomicCalendar:
    """Fetch and filter economic events for forex trading"""
    
    def __init__(self):
        """Initialize economic calendar with free API sources"""
        # Free API endpoints (no key required)
        self.sources = {
            'primary': 'https://nfs.faireconomy.media/ff_calendar_thisweek.json',  # Forex Factory
            'backup': 'https://economic-calendar.tradingview.com/events'  # TradingView
        }
        
        self.cache = {}
        self.cache_time = None
        self.cache_duration = 3600  # Cache for 1 hour
        
        # Impact levels
        self.HIGH_IMPACT = ['High', 'high', 'RED']
        self.MEDIUM_IMPACT = ['Medium', 'medium', 'ORANGE']
        self.LOW_IMPACT = ['Low', 'low', 'YELLOW']
        
    def get_upcoming_events(self, hours_ahead=24, currency=None):
        """
        Get upcoming economic events
        
        Args:
            hours_ahead: Look ahead this many hours
            currency: Filter by currency (e.g., 'USD', 'EUR', 'GBP')
        
        Returns:
            List of events
        """
        # Check cache
        if self._is_cached():
            events = self.cache.get('events', [])
        else:
            # Fetch from API
            events = self._fetch_from_forex_factory()
            if not events:
                events = self._fetch_from_backup()
            
            # Cache results
            self.cache['events'] = events
            self.cache_time = datetime.now()
        
        # Filter events
        filtered = self._filter_events(events, hours_ahead, currency)
        
        return filtered
    
    def _is_cached(self):
        """Check if cache is still valid"""
        if not self.cache_time:
            return False
        
        elapsed = (datetime.now() - self.cache_time).total_seconds()
        return elapsed < self.cache_duration
    
    def _fetch_from_forex_factory(self):
        """Fetch events from Forex Factory"""
        try:
            response = requests.get(self.sources['primary'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                events = []
                for event in data:
                    # Parse event
                    parsed = {
                        'title': event.get('title', ''),
                        'country': event.get('country', ''),
                        'currency': self._get_currency_from_country(event.get('country', '')),
                        'date': event.get('date', ''),
                        'impact': event.get('impact', 'Low'),
                        'forecast': event.get('forecast', ''),
                        'previous': event.get('previous', ''),
                        'source': 'Forex Factory'
                    }
                    events.append(parsed)
                
                return events
            
            return None
            
        except Exception as e:
            print(f"Forex Factory API error: {e}")
            return None
    
    def _fetch_from_backup(self):
        """Fetch from backup source (simplified)"""
        # For now, return empty list as backup
        # In production, implement TradingView or other API
        return []
    
    def _get_currency_from_country(self, country):
        """Map country to currency"""
        currency_map = {
            'USD': ['United States', 'USA', 'US'],
            'EUR': ['European Union', 'EU', 'Eurozone', 'Germany', 'France'],
            'GBP': ['United Kingdom', 'UK', 'Great Britain'],
            'JPY': ['Japan', 'JP'],
            'AUD': ['Australia', 'AU'],
            'CAD': ['Canada', 'CA'],
            'CHF': ['Switzerland', 'CH'],
            'NZD': ['New Zealand', 'NZ']
        }
        
        for currency, countries in currency_map.items():
            if any(c.lower() in country.lower() for c in countries):
                return currency
        
        return 'UNKNOWN'
    
    def _filter_events(self, events, hours_ahead, currency):
        """Filter events by time and currency"""
        if not events:
            return []
        
        # Make timezone-aware
        from datetime import timezone
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours_ahead)
        
        filtered = []
        for event in events:
            # Parse date
            try:
                event_date_str = event['date']
                # Try to parse as ISO format
                if 'Z' in event_date_str or '+' in event_date_str:
                    event_time = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                else:
                    # Assume UTC if no timezone
                    event_time = datetime.fromisoformat(event_date_str).replace(tzinfo=timezone.utc)
            except:
                # Skip if can't parse date
                continue
            
            # Check if within time window
            if now <= event_time <= cutoff:
                # Check currency filter
                if currency is None or event['currency'] == currency:
                    filtered.append(event)
        
        return filtered
    
    def has_high_impact_event(self, currency, hours_ahead=4):
        """
        Check if there's a high-impact event coming up
        
        Args:
            currency: Currency to check (e.g., 'USD', 'EUR')
            hours_ahead: Look ahead this many hours
        
        Returns:
            bool: True if high-impact event found
        """
        events = self.get_upcoming_events(hours_ahead, currency)
        
        for event in events:
            if event['impact'] in self.HIGH_IMPACT:
                return True
        
        return False
    
    def get_next_high_impact_event(self, currency):
        """Get the next high-impact event for a currency"""
        events = self.get_upcoming_events(hours_ahead=168, currency=currency)  # 1 week
        
        for event in events:
            if event['impact'] in self.HIGH_IMPACT:
                return event
        
        return None
    
    def is_safe_to_trade(self, pair, hours_buffer=2):
        """
        Check if it's safe to trade a pair (no high-impact news coming)
        
        Args:
            pair: Forex pair (e.g., 'EURUSD', 'GBPUSD')
            hours_buffer: Avoid trading this many hours before high-impact news
        
        Returns:
            tuple: (is_safe, reason)
        """
        # Extract currencies from pair
        if len(pair) == 6:
            base = pair[:3]
            quote = pair[3:]
        else:
            return (True, "Unknown pair format")
        
        # Check both currencies
        for currency in [base, quote]:
            if self.has_high_impact_event(currency, hours_buffer):
                next_event = self.get_next_high_impact_event(currency)
                if next_event:
                    return (False, f"High-impact {currency} event: {next_event['title']}")
        
        return (True, "No high-impact events")


# Testing
if __name__ == "__main__":
    print("Testing Economic Calendar...")
    print("=" * 60)
    
    calendar = EconomicCalendar()
    
    # Test 1: Get upcoming USD events
    print("\n1. Upcoming USD events (next 24 hours):")
    usd_events = calendar.get_upcoming_events(hours_ahead=24, currency='USD')
    if usd_events:
        for event in usd_events[:5]:  # Show first 5
            print(f"   - {event['title']} ({event['impact']}) at {event['date']}")
    else:
        print("   No USD events found (or API unavailable)")
    
    # Test 2: Check if safe to trade EUR/USD
    print("\n2. Is it safe to trade EUR/USD?")
    is_safe, reason = calendar.is_safe_to_trade('EURUSD', hours_buffer=2)
    print(f"   Safe: {is_safe}")
    print(f"   Reason: {reason}")
    
    # Test 3: Check for high-impact GBP events
    print("\n3. High-impact GBP events coming?")
    has_event = calendar.has_high_impact_event('GBP', hours_ahead=4)
    print(f"   Has high-impact event: {has_event}")
    
    print("\n" + "=" * 60)
    print("[OK] Economic Calendar module ready!")
