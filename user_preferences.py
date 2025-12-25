"""
👤 User Preferences System
Manages user language, timezone, and regional preferences for localization
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class UserPreferences:
    """User preference settings"""
    telegram_id: int
    language: str = 'en'
    timezone: str = 'UTC'
    region: str = 'global'
    notifications_enabled: bool = True
    price_alerts_enabled: bool = False
    session_alerts_enabled: bool = True
    performance_alerts_enabled: bool = False
    trade_alerts_enabled: bool = True
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    risk_tolerance: str = 'medium'  # low, medium, high
    preferred_assets: list = None
    currency_display: str = 'USD'
    date_format: str = 'YYYY-MM-DD'
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.preferred_assets is None:
            self.preferred_assets = ['EURUSD', 'GBPUSD']
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

class UserPreferencesManager:
    """Manages user preferences and localization settings"""

    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.preferences_file = os.path.join(data_dir, 'user_preferences.json')
        self.logger = logging.getLogger(__name__)

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Load existing preferences
        self.preferences = self._load_preferences()

        # Supported options
        self.supported_languages = ['en', 'es', 'ar', 'zh', 'ru', 'pt', 'de', 'fr']
        self.supported_regions = ['us', 'eu', 'asia', 'latin_america', 'middle_east', 'global']
        self.supported_risk_levels = ['low', 'medium', 'high']

    def _load_preferences(self) -> Dict[int, UserPreferences]:
        """Load user preferences from file"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                preferences = {}
                for telegram_id, prefs_dict in data.items():
                    # Convert telegram_id back to int
                    tid = int(telegram_id)
                    # Create UserPreferences object
                    preferences[tid] = UserPreferences(
                        telegram_id=tid,
                        language=prefs_dict.get('language', 'en'),
                        timezone=prefs_dict.get('timezone', 'UTC'),
                        region=prefs_dict.get('region', 'global'),
                        notifications_enabled=prefs_dict.get('notifications_enabled', True),
                        price_alerts_enabled=prefs_dict.get('price_alerts_enabled', False),
                        session_alerts_enabled=prefs_dict.get('session_alerts_enabled', True),
                        performance_alerts_enabled=prefs_dict.get('performance_alerts_enabled', False),
                        trade_alerts_enabled=prefs_dict.get('trade_alerts_enabled', True),
                        quiet_hours_start=prefs_dict.get('quiet_hours_start'),
                        quiet_hours_end=prefs_dict.get('quiet_hours_end'),
                        risk_tolerance=prefs_dict.get('risk_tolerance', 'medium'),
                        preferred_assets=prefs_dict.get('preferred_assets', ['EURUSD', 'GBPUSD']),
                        currency_display=prefs_dict.get('currency_display', 'USD'),
                        date_format=prefs_dict.get('date_format', 'YYYY-MM-DD'),
                        created_at=prefs_dict.get('created_at'),
                        updated_at=prefs_dict.get('updated_at')
                    )

                return preferences

            except Exception as e:
                self.logger.error(f"Failed to load preferences: {e}")
                return {}
        return {}

    def _save_preferences(self):
        """Save user preferences to file"""
        try:
            # Convert preferences to dict format
            data = {}
            for telegram_id, prefs in self.preferences.items():
                data[str(telegram_id)] = asdict(prefs)

            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")

    def get_user_preferences(self, telegram_id: int) -> UserPreferences:
        """Get user preferences, create default if not exists"""
        if telegram_id not in self.preferences:
            self.preferences[telegram_id] = UserPreferences(telegram_id=telegram_id)
            self._save_preferences()

        return self.preferences[telegram_id]

    def update_user_preferences(self, telegram_id: int, **updates) -> bool:
        """Update user preferences"""
        try:
            prefs = self.get_user_preferences(telegram_id)

            # Validate updates
            if 'language' in updates and updates['language'] not in self.supported_languages:
                return False
            if 'region' in updates and updates['region'] not in self.supported_regions:
                return False
            if 'risk_tolerance' in updates and updates['risk_tolerance'] not in self.supported_risk_levels:
                return False

            # Update preferences
            for key, value in updates.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)

            prefs.updated_at = datetime.now().isoformat()
            self._save_preferences()

            return True

        except Exception as e:
            self.logger.error(f"Failed to update preferences for {telegram_id}: {e}")
            return False

    def set_language(self, telegram_id: int, language: str) -> bool:
        """Set user language preference"""
        if language not in self.supported_languages:
            return False
        return self.update_user_preferences(telegram_id, language=language)

    def set_timezone(self, telegram_id: int, timezone: str) -> bool:
        """Set user timezone"""
        try:
            import pytz
            pytz.timezone(timezone)  # Validate timezone
            return self.update_user_preferences(telegram_id, timezone=timezone)
        except:
            return False

    def set_region(self, telegram_id: int, region: str) -> bool:
        """Set user region for regulatory compliance"""
        if region not in self.supported_regions:
            return False
        return self.update_user_preferences(telegram_id, region=region)

    def toggle_notification(self, telegram_id: int, notification_type: str) -> bool:
        """Toggle specific notification type"""
        valid_types = ['price_alerts', 'session_alerts', 'performance_alerts', 'trade_alerts']

        if notification_type not in valid_types:
            return False

        prefs = self.get_user_preferences(telegram_id)
        current_value = getattr(prefs, notification_type + '_enabled')
        return self.update_user_preferences(telegram_id, **{notification_type + '_enabled': not current_value})

    def set_quiet_hours(self, telegram_id: int, start_time: str, end_time: str) -> bool:
        """Set quiet hours for notifications"""
        # Validate time format (HH:MM)
        try:
            datetime.strptime(start_time, '%H:%M')
            datetime.strptime(end_time, '%H:%M')
        except ValueError:
            return False

        return self.update_user_preferences(
            telegram_id,
            quiet_hours_start=start_time,
            quiet_hours_end=end_time
        )

    def add_preferred_asset(self, telegram_id: int, asset: str) -> bool:
        """Add asset to user's preferred assets"""
        prefs = self.get_user_preferences(telegram_id)
        if asset not in prefs.preferred_assets:
            prefs.preferred_assets.append(asset)
            prefs.updated_at = datetime.now().isoformat()
            self._save_preferences()
            return True
        return False

    def remove_preferred_asset(self, telegram_id: int, asset: str) -> bool:
        """Remove asset from user's preferred assets"""
        prefs = self.get_user_preferences(telegram_id)
        if asset in prefs.preferred_assets:
            prefs.preferred_assets.remove(asset)
            prefs.updated_at = datetime.now().isoformat()
            self._save_preferences()
            return True
        return False

    def get_localized_message(self, telegram_id: int, key: str, **kwargs) -> str:
        """Get localized message for user"""
        from localization_system import get_localized_message

        prefs = self.get_user_preferences(telegram_id)
        return get_localized_message(key, prefs.language, **kwargs)

    def should_send_notification(self, telegram_id: int, notification_type: str) -> bool:
        """Check if notification should be sent based on user preferences"""
        prefs = self.get_user_preferences(telegram_id)

        # Check if notifications are enabled globally
        if not prefs.notifications_enabled:
            return False

        # Check specific notification type
        type_enabled = getattr(prefs, notification_type + '_enabled', True)
        if not type_enabled:
            return False

        # Check quiet hours
        if prefs.quiet_hours_start and prefs.quiet_hours_end:
            try:
                import pytz
                from datetime import datetime

                tz = pytz.timezone(prefs.timezone)
                now = datetime.now(tz)

                start_time = datetime.strptime(prefs.quiet_hours_start, '%H:%M').time()
                end_time = datetime.strptime(prefs.quiet_hours_end, '%H:%M').time()

                current_time = now.time()

                # Check if current time is within quiet hours
                if start_time <= end_time:
                    # Same day quiet hours
                    if start_time <= current_time <= end_time:
                        return False
                else:
                    # Overnight quiet hours
                    if current_time >= start_time or current_time <= end_time:
                        return False

            except Exception as e:
                self.logger.warning(f"Error checking quiet hours: {e}")

        return True

    def get_user_region_info(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive regional information for user"""
        from localization_system import get_timezone_info, get_regional_regulation

        prefs = self.get_user_preferences(telegram_id)

        return {
            'language': prefs.language,
            'timezone_info': get_timezone_info(prefs.timezone),
            'region_regulation': get_regional_regulation(prefs.region),
            'preferences': {
                'risk_tolerance': prefs.risk_tolerance,
                'currency_display': prefs.currency_display,
                'date_format': prefs.date_format,
                'preferred_assets': prefs.preferred_assets
            }
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_users = len(self.preferences)
        language_counts = {}
        region_counts = {}

        for prefs in self.preferences.values():
            language_counts[prefs.language] = language_counts.get(prefs.language, 0) + 1
            region_counts[prefs.region] = region_counts.get(prefs.region, 0) + 1

        return {
            'total_users': total_users,
            'language_distribution': language_counts,
            'region_distribution': region_counts,
            'most_popular_language': max(language_counts, key=language_counts.get) if language_counts else 'en',
            'most_popular_region': max(region_counts, key=region_counts.get) if region_counts else 'global'
        }

# Global instance
user_prefs = UserPreferencesManager()

# Convenience functions
def get_user_prefs(telegram_id: int) -> UserPreferences:
    """Get user preferences"""
    return user_prefs.get_user_preferences(telegram_id)

def update_user_prefs(telegram_id: int, **updates) -> bool:
    """Update user preferences"""
    return user_prefs.update_user_preferences(telegram_id, **updates)

def get_localized_msg(telegram_id: int, key: str, **kwargs) -> str:
    """Get localized message for user"""
    return user_prefs.get_localized_message(telegram_id, key, **kwargs)

if __name__ == "__main__":
    # Test the user preferences system
    print("👤 User Preferences System Test")
    print("=" * 50)

    # Test creating preferences
    test_user_id = 123456789
    prefs = get_user_prefs(test_user_id)
    print(f"Default preferences for user {test_user_id}:")
    print(f"  Language: {prefs.language}")
    print(f"  Timezone: {prefs.timezone}")
    print(f"  Region: {prefs.region}")

    # Test updating preferences
    success = update_user_prefs(test_user_id, language='es', timezone='America/Mexico_City')
    print(f"\nUpdated preferences: {success}")

    updated_prefs = get_user_prefs(test_user_id)
    print(f"  Language: {updated_prefs.language}")
    print(f"  Timezone: {updated_prefs.timezone}")

    # Test localized message
    message = get_localized_msg(test_user_id, 'welcome')
    print(f"\nLocalized welcome message: {message[:100]}...")

    # Test statistics
    stats = user_prefs.get_statistics()
    print(f"\nStatistics: {stats}")

    print("\nUser preferences system test completed!")
