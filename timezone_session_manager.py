"""
Timezone and Market Session Manager
Handles timezone-aware trading hours, market sessions, and regional time management
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
from functools import lru_cache

class TimezoneSessionManager:
    """Manages timezone-aware market sessions and trading hours"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Major market timezones
        self.market_timezones = {
            'tokyo': 'Asia/Tokyo',           # Japan, Australia (some)
            'sydney': 'Australia/Sydney',    # Australia
            'shanghai': 'Asia/Shanghai',     # China
            'hong_kong': 'Asia/Hong_Kong',   # Hong Kong
            'singapore': 'Asia/Singapore',   # Singapore
            'london': 'Europe/London',       # UK, Europe
            'zurich': 'Europe/Zurich',       # Switzerland
            'frankfurt': 'Europe/Berlin',    # Germany, EU
            'new_york': 'America/New_York',  # US East Coast
            'chicago': 'America/Chicago',    # US Central
            'los_angeles': 'America/Los_Angeles',  # US West Coast
            'sao_paulo': 'America/Sao_Paulo', # Brazil
            'mexico_city': 'America/Mexico_City', # Mexico
            'utc': 'UTC'                     # Universal reference
        }

        # Market session definitions (in local timezone, then converted to UTC)
        self.market_sessions = {
            'tokyo_session': {
                'name': 'Tokyo Session',
                'timezone': 'Asia/Tokyo',
                'local_start': time(9, 0),    # 09:00 JST
                'local_end': time(15, 0),     # 15:00 JST
                'markets': ['JPY', 'CNY'],
                'importance': 'primary'
            },
            'london_session': {
                'name': 'London Session',
                'timezone': 'Europe/London',
                'local_start': time(8, 0),    # 08:00 GMT/BST
                'local_end': time(16, 30),    # 16:30 GMT/BST
                'markets': ['EUR', 'GBP'],
                'importance': 'primary'
            },
            'new_york_session': {
                'name': 'New York Session',
                'timezone': 'America/New_York',
                'local_start': time(9, 30),   # 09:30 EST/EDT
                'local_end': time(16, 0),     # 16:00 EST/EDT
                'markets': ['USD', 'CAD'],
                'importance': 'primary'
            },
            'sydney_session': {
                'name': 'Sydney Session',
                'timezone': 'Australia/Sydney',
                'local_start': time(10, 0),   # 10:00 AEST/AEDT
                'local_end': time(16, 0),     # 16:00 AEST/AEDT
                'markets': ['AUD'],
                'importance': 'secondary'
            },
            'sao_paulo_session': {
                'name': 'São Paulo Session',
                'timezone': 'America/Sao_Paulo',
                'local_start': time(9, 0),    # 09:00 BRT/BRST
                'local_end': time(17, 0),     # 17:00 BRT/BRST
                'markets': ['BRL'],
                'importance': 'secondary'
            },
            'hong_kong_session': {
                'name': 'Hong Kong Session',
                'timezone': 'Asia/Hong_Kong',
                'local_start': time(9, 30),   # 09:30 HKT
                'local_end': time(16, 0),     # 16:00 HKT
                'markets': ['CNY', 'HKD'],
                'importance': 'secondary'
            }
        }

        # Holiday schedules (simplified - would need to be updated regularly)
        self.market_holidays = {
            'us': ['2024-01-01', '2024-01-15', '2024-02-19', '2024-03-29', '2024-05-27', '2024-07-04', '2024-09-02', '2024-11-11', '2024-11-28', '2024-12-25'],
            'eu': ['2024-01-01', '2024-04-01', '2024-05-01', '2024-12-25', '2024-12-26'],
            'jp': ['2024-01-01', '2024-01-08', '2024-02-11', '2024-02-12', '2024-02-23', '2024-03-20', '2024-04-29', '2024-05-03', '2024-05-06', '2024-07-15', '2024-08-11', '2024-08-12', '2024-09-16', '2024-09-23', '2024-10-14', '2024-11-03', '2024-11-23', '2024-12-31'],
            'au': ['2024-01-01', '2024-01-26', '2024-03-29', '2024-04-25', '2024-06-10', '2024-08-05', '2024-10-07', '2024-12-25', '2024-12-26'],
            'cn': ['2024-01-01', '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13', '2024-04-05', '2024-05-01', '2024-05-02', '2024-05-03', '2024-06-10', '2024-09-15', '2024-09-16', '2024-09-17', '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05', '2024-10-06', '2024-10-07', '2024-12-25', '2024-12-26', '2024-12-27']
        }

    def get_current_sessions(self, include_upcoming: bool = True) -> Dict:
        """Get currently active market sessions"""
        try:
            now_utc = datetime.now(pytz.UTC)
            active_sessions = []
            upcoming_sessions = []

            for session_key, session_info in self.market_sessions.items():
                session_status = self._get_session_status(session_info, now_utc)

                if session_status['is_active']:
                    active_sessions.append({
                        'session_key': session_key,
                        'name': session_info['name'],
                        'markets': session_info['markets'],
                        'importance': session_info['importance'],
                        'time_remaining': session_status['time_remaining'],
                        'progress_percent': session_status['progress_percent']
                    })
                elif include_upcoming and session_status['next_start']:
                    upcoming_sessions.append({
                        'session_key': session_key,
                        'name': session_info['name'],
                        'markets': session_info['markets'],
                        'next_start': session_status['next_start'],
                        'hours_until': session_status['hours_until']
                    })

            # Sort upcoming by soonest first
            upcoming_sessions.sort(key=lambda x: x['hours_until'])

            return {
                'active_sessions': active_sessions,
                'upcoming_sessions': upcoming_sessions[:3],  # Next 3 upcoming
                'current_utc_time': now_utc.isoformat(),
                'total_active': len(active_sessions),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error getting current sessions: {e}")
            return self._error_result(str(e))

    def get_session_schedule(self, session_key: str = None) -> Dict:
        """Get detailed schedule for a specific session or all sessions"""
        try:
            if session_key:
                if session_key not in self.market_sessions:
                    return self._error_result(f"Session '{session_key}' not found")

                session_info = self.market_sessions[session_key]
                schedule = self._calculate_session_schedule(session_info)

                return {
                    'session_key': session_key,
                    'name': session_info['name'],
                    'timezone': session_info['timezone'],
                    'schedule': schedule,
                    'markets': session_info['markets'],
                    'importance': session_info['importance'],
                    'status': 'success'
                }
            else:
                # Return all sessions
                all_schedules = {}
                for key, session_info in self.market_sessions.items():
                    all_schedules[key] = {
                        'name': session_info['name'],
                        'timezone': session_info['timezone'],
                        'markets': session_info['markets'],
                        'importance': session_info['importance'],
                        'schedule': self._calculate_session_schedule(session_info)
                    }

                return {
                    'sessions': all_schedules,
                    'total_sessions': len(all_schedules),
                    'status': 'success'
                }

        except Exception as e:
            self.logger.error(f"Error getting session schedule: {e}")
            return self._error_result(str(e))

    def convert_time_between_timezones(self, time_input: datetime, from_tz: str, to_tz: str) -> datetime:
        """Convert time between different timezones"""
        try:
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)

            # Localize the input time
            if time_input.tzinfo is None:
                localized_time = from_timezone.localize(time_input)
            else:
                localized_time = time_input.astimezone(from_timezone)

            # Convert to target timezone
            converted_time = localized_time.astimezone(to_timezone)

            return converted_time

        except Exception as e:
            self.logger.error(f"Error converting time: {e}")
            return time_input

    def get_market_timezone_info(self, market_code: str) -> Dict:
        """Get timezone information for a specific market"""
        try:
            # Map market codes to timezones
            market_timezone_map = {
                'USD': 'America/New_York',
                'EUR': 'Europe/London',
                'GBP': 'Europe/London',
                'JPY': 'Asia/Tokyo',
                'CNY': 'Asia/Shanghai',
                'AUD': 'Australia/Sydney',
                'CAD': 'America/New_York',
                'CHF': 'Europe/Zurich',
                'BRL': 'America/Sao_Paulo',
                'HKD': 'Asia/Hong_Kong',
                'SGD': 'Asia/Singapore'
            }

            timezone_name = market_timezone_map.get(market_code, 'UTC')
            tz = pytz.timezone(timezone_name)

            now_utc = datetime.now(pytz.UTC)
            now_local = now_utc.astimezone(tz)

            return {
                'market_code': market_code,
                'timezone_name': timezone_name,
                'timezone_offset': now_local.utcoffset().total_seconds() / 3600,
                'current_local_time': now_local.isoformat(),
                'current_utc_time': now_utc.isoformat(),
                'is_dst': bool(now_local.dst()),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error getting timezone info for {market_code}: {e}")
            return self._error_result(str(e))

    def is_market_open(self, market_code: str) -> Dict:
        """Check if a specific market is currently open"""
        try:
            # Get the relevant sessions for this market
            relevant_sessions = []
            for session_key, session_info in self.market_sessions.items():
                if market_code in session_info['markets']:
                    relevant_sessions.append(session_key)

            if not relevant_sessions:
                return {
                    'market_code': market_code,
                    'is_open': False,
                    'reason': 'No sessions found for this market',
                    'next_open': None,
                    'status': 'success'
                }

            now_utc = datetime.now(pytz.UTC)
            is_open = False
            next_open_time = None
            active_session = None

            for session_key in relevant_sessions:
                session_info = self.market_sessions[session_key]
                status = self._get_session_status(session_info, now_utc)

                if status['is_active']:
                    is_open = True
                    active_session = session_key
                    break
                elif status['next_start'] and (next_open_time is None or status['next_start'] < next_open_time):
                    next_open_time = status['next_start']

            return {
                'market_code': market_code,
                'is_open': is_open,
                'active_session': active_session,
                'next_open': next_open_time.isoformat() if next_open_time else None,
                'sessions_checked': relevant_sessions,
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error checking if market {market_code} is open: {e}")
            return self._error_result(str(e))

    def get_trading_hours_summary(self) -> Dict:
        """Get a summary of all trading hours and current status"""
        try:
            now_utc = datetime.now(pytz.UTC)
            session_summary = []

            for session_key, session_info in self.market_sessions.items():
                status = self._get_session_status(session_info, now_utc)
                tz = pytz.timezone(session_info['timezone'])

                # Get local times
                today = now_utc.date()
                local_start = tz.localize(datetime.combine(today, session_info['local_start']))
                local_end = tz.localize(datetime.combine(today, session_info['local_end']))

                # Convert to UTC for comparison
                utc_start = local_start.astimezone(pytz.UTC)
                utc_end = local_end.astimezone(pytz.UTC)

                session_summary.append({
                    'session_key': session_key,
                    'name': session_info['name'],
                    'is_active': status['is_active'],
                    'local_timezone': session_info['timezone'],
                    'local_start': local_start.strftime('%H:%M %Z'),
                    'local_end': local_end.strftime('%H:%M %Z'),
                    'utc_start': utc_start.strftime('%H:%M UTC'),
                    'utc_end': utc_end.strftime('%H:%M UTC'),
                    'markets': session_info['markets'],
                    'importance': session_info['importance'],
                    'time_remaining': status.get('time_remaining', 0),
                    'progress_percent': status.get('progress_percent', 0)
                })

            # Sort by UTC start time
            session_summary.sort(key=lambda x: x['utc_start'])

            return {
                'current_utc_time': now_utc.isoformat(),
                'sessions': session_summary,
                'active_count': sum(1 for s in session_summary if s['is_active']),
                'total_sessions': len(session_summary),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Error getting trading hours summary: {e}")
            return self._error_result(str(e))

    def get_market_holidays(self, region: str = None) -> Dict:
        """Get holiday schedule for markets"""
        try:
            if region:
                if region not in self.market_holidays:
                    return self._error_result(f"Region '{region}' not found")

                return {
                    'region': region,
                    'holidays': self.market_holidays[region],
                    'total_holidays': len(self.market_holidays[region]),
                    'status': 'success'
                }
            else:
                return {
                    'regions': self.market_holidays,
                    'total_regions': len(self.market_holidays),
                    'status': 'success'
                }

        except Exception as e:
            self.logger.error(f"Error getting market holidays: {e}")
            return self._error_result(str(e))

    def _get_session_status(self, session_info: Dict, current_time: datetime) -> Dict:
        """Get detailed status of a market session"""
        try:
            tz = pytz.timezone(session_info['timezone'])

            # Get today's session times
            today = current_time.date()
            local_start = tz.localize(datetime.combine(today, session_info['local_start']))
            local_end = tz.localize(datetime.combine(today, session_info['local_end']))

            # Convert to UTC
            utc_start = local_start.astimezone(pytz.UTC)
            utc_end = local_end.astimezone(pytz.UTC)

            # Check if session spans midnight
            if utc_start > utc_end:
                # Session goes into next day
                if current_time >= utc_start or current_time <= utc_end:
                    is_active = True
                else:
                    is_active = False
            else:
                is_active = utc_start <= current_time <= utc_end

            result = {'is_active': is_active}

            if is_active:
                # Calculate time remaining and progress
                if utc_start > utc_end:  # Spans midnight
                    if current_time >= utc_start:
                        elapsed = (current_time - utc_start).total_seconds()
                        total_duration = (datetime.combine(today + timedelta(days=1), session_info['local_end']) - datetime.combine(today, session_info['local_start'])).total_seconds()
                    else:
                        elapsed = (current_time - (utc_end - timedelta(days=1))).total_seconds()
                        total_duration = (utc_end - utc_start).total_seconds()
                else:
                    elapsed = (current_time - utc_start).total_seconds()
                    total_duration = (utc_end - utc_start).total_seconds()

                time_remaining = max(0, total_duration - elapsed)
                progress_percent = min(100, (elapsed / total_duration) * 100) if total_duration > 0 else 0

                result.update({
                    'time_remaining': int(time_remaining // 60),  # minutes
                    'progress_percent': round(progress_percent, 1)
                })
            else:
                # Find next session start
                next_start = self._get_next_session_start(session_info, current_time)
                hours_until = ((next_start - current_time).total_seconds() / 3600) if next_start else None

                result.update({
                    'next_start': next_start,
                    'hours_until': round(hours_until, 1) if hours_until else None
                })

            return result

        except Exception as e:
            self.logger.error(f"Error getting session status: {e}")
            return {'is_active': False, 'error': str(e)}

    def _get_next_session_start(self, session_info: Dict, current_time: datetime) -> Optional[datetime]:
        """Calculate the next session start time"""
        try:
            tz = pytz.timezone(session_info['timezone'])
            today = current_time.date()

            # Check if today is a holiday
            region = self._get_region_for_session(session_info)
            if region and self._is_holiday(today, region):
                # Skip holidays, find next non-holiday
                for days_ahead in range(1, 8):  # Check next week
                    check_date = today + timedelta(days=days_ahead)
                    if not self._is_holiday(check_date, region):
                        today = check_date
                        break

            local_start = tz.localize(datetime.combine(today, session_info['local_start']))
            utc_start = local_start.astimezone(pytz.UTC)

            if utc_start > current_time:
                return utc_start
            else:
                # Session already passed today, get tomorrow's
                tomorrow = today + timedelta(days=1)
                local_start = tz.localize(datetime.combine(tomorrow, session_info['local_start']))

                # Skip weekends and holidays
                while local_start.weekday() >= 5 or self._is_holiday(local_start.date(), region):  # 5=Saturday, 6=Sunday
                    local_start = tz.localize(datetime.combine(local_start.date() + timedelta(days=1), session_info['local_start']))

                return local_start.astimezone(pytz.UTC)

        except Exception as e:
            self.logger.error(f"Error calculating next session start: {e}")
            return None

    def _calculate_session_schedule(self, session_info: Dict) -> Dict:
        """Calculate detailed schedule for a session"""
        try:
            tz = pytz.timezone(session_info['timezone'])
            now_utc = datetime.now(pytz.UTC)

            # Get today's schedule
            today = now_utc.date()
            local_start = tz.localize(datetime.combine(today, session_info['local_start']))
            local_end = tz.localize(datetime.combine(today, session_info['local_end']))

            utc_start = local_start.astimezone(pytz.UTC)
            utc_end = local_end.astimezone(pytz.UTC)

            # Handle sessions that span midnight
            if utc_start > utc_end:
                utc_end = utc_end + timedelta(days=1)

            # Weekly schedule (assuming Mon-Fri)
            weekly_schedule = []
            for day_offset in range(7):
                day = today + timedelta(days=day_offset)
                day_name = day.strftime('%A')

                if day.weekday() < 5:  # Monday to Friday
                    day_start = tz.localize(datetime.combine(day, session_info['local_start']))
                    day_end = tz.localize(datetime.combine(day, session_info['local_end']))

                    weekly_schedule.append({
                        'day': day_name,
                        'date': day.isoformat(),
                        'local_start': day_start.strftime('%H:%M %Z'),
                        'local_end': day_end.strftime('%H:%M %Z'),
                        'utc_start': day_start.astimezone(pytz.UTC).strftime('%H:%M UTC'),
                        'utc_end': day_end.astimezone(pytz.UTC).strftime('%H:%M UTC'),
                        'is_today': day == today
                    })

            return {
                'timezone': session_info['timezone'],
                'local_start_time': session_info['local_start'].strftime('%H:%M'),
                'local_end_time': session_info['local_end'].strftime('%H:%M'),
                'utc_start_time': utc_start.strftime('%H:%M UTC'),
                'utc_end_time': utc_end.strftime('%H:%M UTC'),
                'duration_hours': (utc_end - utc_start).total_seconds() / 3600,
                'weekly_schedule': weekly_schedule,
                'current_status': self._get_session_status(session_info, now_utc)
            }

        except Exception as e:
            self.logger.error(f"Error calculating session schedule: {e}")
            return {'error': str(e)}

    def _get_region_for_session(self, session_info: Dict) -> Optional[str]:
        """Get the region code for a session based on its timezone"""
        timezone_region_map = {
            'Asia/Tokyo': 'jp',
            'Asia/Shanghai': 'cn',
            'Europe/London': 'eu',
            'America/New_York': 'us',
            'Australia/Sydney': 'au',
            'America/Sao_Paulo': 'br'
        }

        return timezone_region_map.get(session_info['timezone'])

    def _is_holiday(self, date: datetime.date, region: str) -> bool:
        """Check if a date is a holiday in a region"""
        try:
            holidays = self.market_holidays.get(region, [])
            date_str = date.isoformat()
            return date_str in holidays
        except Exception:
            return False

    def _error_result(self, message: str) -> Dict:
        """Return standardized error result"""
        return {
            'status': 'error',
            'message': message,
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }

# Global instance
timezone_manager = TimezoneSessionManager()

# Convenience functions
def get_current_sessions(include_upcoming: bool = True) -> Dict:
    """Convenience function for current sessions"""
    return timezone_manager.get_current_sessions(include_upcoming)

def get_session_schedule(session_key: str = None) -> Dict:
    """Convenience function for session schedules"""
    return timezone_manager.get_session_schedule(session_key)

def get_market_timezone_info(market_code: str) -> Dict:
    """Convenience function for market timezone info"""
    return timezone_manager.get_market_timezone_info(market_code)

def is_market_open(market_code: str) -> Dict:
    """Convenience function to check if market is open"""
    return timezone_manager.is_market_open(market_code)

def get_trading_hours_summary() -> Dict:
    """Convenience function for trading hours summary"""
    return timezone_manager.get_trading_hours_summary()

def get_market_holidays(region: str = None) -> Dict:
    """Convenience function for market holidays"""
    return timezone_manager.get_market_holidays(region)

# Example usage
if __name__ == "__main__":
    print("Timezone Session Manager Test")
    print("=" * 50)

    # Test current sessions
    print("\n1. Current Active Sessions:")
    sessions = get_current_sessions()
    if sessions.get('status') == 'success':
        active = sessions.get('active_sessions', [])
        if active:
            for session in active:
                print(f"  🟢 {session['name']}: {', '.join(session['markets'])} ({session['time_remaining']}min remaining)")
        else:
            print("  No active sessions")

        upcoming = sessions.get('upcoming_sessions', [])
        if upcoming:
            print("\n  📅 Upcoming Sessions:")
            for session in upcoming[:2]:
                print(f"  • {session['name']}: {session['hours_until']} hours")
    else:
        print(f"  Error: {sessions.get('message')}")

    # Test market status
    print("\n2. Market Status Check:")
    for market in ['EUR', 'JPY', 'AUD', 'BRL']:
        status = is_market_open(market)
        if status.get('status') == 'success':
            open_status = "🟢 OPEN" if status['is_open'] else "🔴 CLOSED"
            session = f" ({status['active_session']})" if status['active_session'] else ""
            print(f"  {market}: {open_status}{session}")

    # Test trading hours summary
    print("\n3. Trading Hours Summary:")
    hours = get_trading_hours_summary()
    if hours.get('status') == 'success':
        print(f"  Current UTC time: {hours['current_utc_time'][:19]}")
        print(f"  Active sessions: {hours['active_count']}/{hours['total_sessions']}")

    print("\nTimezone Session Manager test completed!")
