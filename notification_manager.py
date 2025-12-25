"""
Notification Manager Module
Handles all types of user notifications including:
- Threshold alerts (18/20, 19/20 criteria warnings)
- Price alerts (custom price levels)
- Session notifications (trading session reminders)
- Performance summaries (weekly digests)
- Trade management reminders (move SL, take profits)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

class NotificationManager:
    def __init__(self, data_file="user_notifications.json"):
        self.data_file = data_file
        self.user_preferences = {}
        self.price_alerts = {}  # {user_id: [{pair, price, direction, created_at}]}
        self.pending_notifications = []
        self.load_data()
    
    def load_data(self):
        """Load user preferences and alerts"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.user_preferences = data.get('preferences', {})
                    self.price_alerts = data.get('price_alerts', {})
            except:
                self.user_preferences = {}
                self.price_alerts = {}
    
    def save_data(self):
        """Save user preferences and alerts"""
        data = {
            'preferences': self.user_preferences,
            'price_alerts': self.price_alerts
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ============================================================================
    # USER PREFERENCES
    # ============================================================================
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get notification preferences for a user"""
        user_id_str = str(user_id)
        if user_id_str not in self.user_preferences:
            # Default preferences
            self.user_preferences[user_id_str] = {
                'threshold_alerts': True,  # 18/20, 19/20 criteria
                'price_alerts': True,
                'session_notifications': True,
                'performance_summaries': True,
                'trade_reminders': True,
                'quiet_hours_enabled': False,
                'quiet_hours_start': '22:00',  # 10 PM
                'quiet_hours_end': '07:00',    # 7 AM
                'last_weekly_summary': None,
                'last_session_notification': None
            }
            self.save_data()
        return self.user_preferences[user_id_str]
    
    def update_user_preference(self, user_id: int, setting: str, value):
        """Update a specific preference"""
        prefs = self.get_user_preferences(user_id)
        prefs[setting] = value
        self.save_data()
    
    def is_quiet_hours(self, user_id: int) -> bool:
        """Check if current time is in user's quiet hours"""
        prefs = self.get_user_preferences(user_id)
        if not prefs['quiet_hours_enabled']:
            return False
        
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        start = prefs['quiet_hours_start']
        end = prefs['quiet_hours_end']
        
        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if start > end:
            return current_time >= start or current_time <= end
        else:
            return start <= current_time <= end
    
    # ============================================================================
    # THRESHOLD ALERTS (18/20, 19/20 criteria warnings)
    # ============================================================================
    
    def should_send_threshold_alert(self, user_id: int, pair: str, criteria_passed: int, criteria_total: int) -> bool:
        """Check if threshold alert should be sent"""
        prefs = self.get_user_preferences(user_id)
        
        if not prefs['threshold_alerts']:
            return False
        
        if self.is_quiet_hours(user_id):
            return False
        
        # Alert at 18/20 (90%) and 19/20 (95%)
        if criteria_total == 20:
            return criteria_passed in [18, 19]
        elif criteria_total == 17:
            return criteria_passed in [15, 16]  # Equivalent for BTC/Gold
        
        return False
    
    def create_threshold_alert_message(self, pair: str, criteria_passed: int, criteria_total: int, progress_pct: float) -> str:
        """Create threshold alert message"""
        msg = f"🔔 *THRESHOLD ALERT*\n\n"
        msg += f"*{pair}* is close to signal!\n\n"
        msg += f"Progress: *{progress_pct:.0f}%*\n"
        msg += f"Criteria: *{criteria_passed}/{criteria_total}*\n\n"
        
        if criteria_passed == criteria_total - 2:
            msg += f"⚠️ *2 criteria away* from A+ signal!\n"
            msg += f"Stay alert and monitor closely.\n"
        elif criteria_passed == criteria_total - 1:
            msg += f"🚨 *1 criterion away* from A+ signal!\n"
            msg += f"Get ready to trade!\n"
        
        msg += f"\n💡 Use `/{pair.lower()}` to check details"
        return msg
    
    # ============================================================================
    # PRICE ALERTS (custom price levels)
    # ============================================================================
    
    def add_price_alert(self, user_id: int, pair: str, price: float, direction: str) -> int:
        """Add a price alert for user
        
        Args:
            user_id: Telegram user ID
            pair: Trading pair (e.g., 'EURUSD', 'BTC')
            price: Target price
            direction: 'above' or 'below'
        
        Returns:
            alert_id: Unique ID for this alert
        """
        user_id_str = str(user_id)
        if user_id_str not in self.price_alerts:
            self.price_alerts[user_id_str] = []
        
        alert_id = len(self.price_alerts[user_id_str]) + 1
        alert = {
            'id': alert_id,
            'pair': pair.upper(),
            'price': price,
            'direction': direction.lower(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'triggered': False
        }
        
        self.price_alerts[user_id_str].append(alert)        
        self.save_data()
        return alert_id
    
    def set_price_alert(self, user_id: int, pair: str, price: float, direction: str):
        """Alias for add_price_alert for compatibility"""
        return self.add_price_alert(user_id, pair, price, direction)
    
    def remove_price_alert(self, user_id: int, alert_id: int) -> bool:
        """Remove a price alert"""
        user_id_str = str(user_id)
        if user_id_str not in self.price_alerts:
            return False
        
        alerts = self.price_alerts[user_id_str]
        for i, alert in enumerate(alerts):
            if alert['id'] == alert_id:
                del alerts[i]
                self.save_data()
                return True
        return False
    
    def get_user_price_alerts(self, user_id: int) -> List[Dict]:
        """Get all price alerts for a user"""
        user_id_str = str(user_id)
        return self.price_alerts.get(user_id_str, [])
    
    def check_price_alerts(self, user_id: int, pair: str, current_price: float) -> List[Dict]:
        """Check if any price alerts should trigger
        
        Returns:
            List of triggered alerts
        """
        user_id_str = str(user_id)
        if user_id_str not in self.price_alerts:
            return []
        
        prefs = self.get_user_preferences(user_id)
        if not prefs['price_alerts'] or self.is_quiet_hours(user_id):
            return []
        
        triggered = []
        alerts = self.price_alerts[user_id_str]
        
        for alert in alerts:
            if alert['triggered']:
                continue
            
            if alert['pair'] != pair.upper():
                continue
            
            # Check if alert triggered
            should_trigger = False
            if alert['direction'] == 'above' and current_price >= alert['price']:
                should_trigger = True
            elif alert['direction'] == 'below' and current_price <= alert['price']:
                should_trigger = True
            
            if should_trigger:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                triggered.append(alert)
        
        if triggered:
            self.save_data()
        
        return triggered
    
    def create_price_alert_message(self, alert: Dict, current_price: float) -> str:
        """Create price alert message"""
        msg = f"🎯 *PRICE ALERT TRIGGERED*\n\n"
        msg += f"*{alert['pair']}* reached your target!\n\n"
        msg += f"Target: ${alert['price']:,.2f}\n"
        msg += f"Current: ${current_price:,.2f}\n"
        msg += f"Direction: {alert['direction'].upper()}\n\n"
        msg += f"💡 Use `/{alert['pair'].lower()}` to check for signal"
        return msg
    
    # ============================================================================
    # SESSION NOTIFICATIONS (trading session reminders)
    # ============================================================================
    
    def get_next_session_time(self) -> Optional[Dict]:
        """Get next upcoming trading session
        
        Returns:
            Dict with session info or None
        """
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        sessions = [
            {'name': 'Tokyo', 'hour': 19, 'minute': 0, 'pairs': ['USD/JPY', 'AUD/USD']},  # 7:00 PM EST
            {'name': 'London', 'hour': 3, 'minute': 0, 'pairs': ['EUR/USD', 'GBP/USD']},  # 3:00 AM EST
            {'name': 'New York', 'hour': 8, 'minute': 0, 'pairs': ['All USD pairs']},     # 8:00 AM EST
            {'name': 'London/NY Overlap', 'hour': 8, 'minute': 0, 'pairs': ['Best for all']},  # 8:00 AM EST
        ]
        
        for session in sessions:
            session_time = now.replace(hour=session['hour'], minute=session['minute'], second=0, microsecond=0)
            
            # If session time has passed today, move to tomorrow
            if session_time < now:
                session_time += timedelta(days=1)
            
            time_until = (session_time - now).total_seconds() / 60  # minutes
            
            # Notify 10 minutes before session
            if 9 <= time_until <= 11:
                return {
                    'name': session['name'],
                    'time': session_time,
                    'pairs': session['pairs'],
                    'minutes_until': int(time_until)
                }
        
        return None
    
    def should_send_session_notification(self, user_id: int) -> bool:
        """Check if session notification should be sent"""
        prefs = self.get_user_preferences(user_id)
        
        if not prefs['session_notifications']:
            return False
        
        if self.is_quiet_hours(user_id):
            return False
        
        # Don't send multiple notifications within 1 hour
        last_notif = prefs.get('last_session_notification')
        if last_notif:
            try:
                last_time = datetime.strptime(last_notif, '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - last_time).total_seconds() < 3600:  # 1 hour
                    return False
            except:
                pass
        
        return True
    
    def create_session_notification_message(self, session_info: Dict) -> str:
        """Create session notification message"""
        msg = f"⏰ *TRADING SESSION ALERT*\n\n"
        msg += f"*{session_info['name']} Session* opening in {session_info['minutes_until']} minutes!\n\n"
        msg += f"📊 *Best Pairs:*\n"
        for pair in session_info['pairs']:
            msg += f"• {pair}\n"
        msg += f"\n💡 Check `/signals` for current setups"
        return msg
    
    # ============================================================================
    # PERFORMANCE SUMMARIES (weekly digests)
    # ============================================================================
    
    def should_send_weekly_summary(self, user_id: int) -> bool:
        """Check if weekly summary should be sent"""
        prefs = self.get_user_preferences(user_id)
        
        if not prefs['performance_summaries']:
            return False
        
        last_summary = prefs.get('last_weekly_summary')
        if not last_summary:
            return True
        
        try:
            last_time = datetime.strptime(last_summary, '%Y-%m-%d')
            days_since = (datetime.now() - last_time).days
            return days_since >= 7
        except:
            return True
    
    def create_weekly_summary_message(self, stats: Dict) -> str:
        """Create weekly performance summary
        
        Args:
            stats: Dict with win_rate, total_signals, total_pips, best_pair, etc.
        """
        msg = f"📊 *WEEKLY PERFORMANCE SUMMARY*\n\n"
        msg += f"*Trading Week:* {stats.get('week_start')} - {stats.get('week_end')}\n\n"
        
        msg += f"*📈 RESULTS:*\n"
        msg += f"Win Rate: *{stats.get('win_rate', 0):.1f}%*\n"
        msg += f"Total Signals: {stats.get('total_signals', 0)}\n"
        msg += f"Wins: {stats.get('wins', 0)} | Losses: {stats.get('losses', 0)}\n"
        msg += f"Pips Captured: *+{stats.get('total_pips', 0)}*\n\n"
        
        if 'best_pair' in stats:
            msg += f"*🏆 BEST PERFORMER:*\n"
            msg += f"{stats['best_pair']}: {stats['best_pair_winrate']:.0f}% win rate\n\n"
        
        if 'improvement_tip' in stats:
            msg += f"*💡 IMPROVEMENT TIP:*\n"
            msg += f"{stats['improvement_tip']}\n\n"
        
        msg += f"Keep up the great work! 🚀"
        return msg
    
    # ============================================================================
    # TRADE MANAGEMENT REMINDERS
    # ============================================================================
    
    def create_breakeven_reminder(self, pair: str, trade_id: int, tp1_hit: bool) -> str:
        """Create reminder to move SL to breakeven"""
        msg = f"💡 *TRADE MANAGEMENT REMINDER*\n\n"
        if tp1_hit:
            msg += f"✅ TP1 hit on *{pair}* (Trade #{trade_id})!\n\n"
            msg += f"*Action Needed:*\n"
            msg += f"Move your Stop Loss to *BREAKEVEN*\n\n"
            msg += f"This makes the trade risk-free and locks in partial profit!\n"
        else:
            msg += f"Trade #{trade_id} ({pair}) is in profit.\n\n"
            msg += f"Consider moving SL closer to entry or to breakeven to protect gains."
        return msg
    
    def create_partial_profit_reminder(self, pair: str, trade_id: int, current_profit_pct: float) -> str:
        """Create reminder to take partial profits"""
        msg = f"💰 *PROFIT TAKING REMINDER*\n\n"
        msg += f"Trade #{trade_id} ({pair}) is up {current_profit_pct:.1f}%!\n\n"
        msg += f"*Consider:*\n"
        msg += f"• Taking 50% profit now\n"
        msg += f"• Moving SL to breakeven\n"
        msg += f"• Letting remaining 50% run to TP2\n\n"
        msg += f"Locking in profits reduces stress and improves win rate!"
        return msg
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def cleanup_old_alerts(self, days_old: int = 30):
        """Remove triggered alerts older than X days"""
        cutoff = datetime.now() - timedelta(days=days_old)
        
        for user_id_str in self.price_alerts:
            alerts = self.price_alerts[user_id_str]
            cleaned_alerts = []
            
            for alert in alerts:
                if not alert['triggered']:
                    cleaned_alerts.append(alert)
                else:
                    try:
                        triggered_at = datetime.strptime(alert['triggered_at'], '%Y-%m-%d %H:%M:%S')
                        if triggered_at > cutoff:
                            cleaned_alerts.append(alert)
                    except:
                        pass
            
            self.price_alerts[user_id_str] = cleaned_alerts
        
        self.save_data()
    
    def get_notification_stats(self, user_id: int) -> Dict:
        """Get notification statistics for a user"""
        prefs = self.get_user_preferences(user_id)
        price_alerts = self.get_user_price_alerts(user_id)
        
        return {
            'enabled_notifications': sum([
                prefs['threshold_alerts'],
                prefs['price_alerts'],
                prefs['session_notifications'],
                prefs['performance_summaries'],
                prefs['trade_reminders']
            ]),
            'total_notifications': 5,
            'active_price_alerts': len([a for a in price_alerts if not a['triggered']]),
            'triggered_price_alerts': len([a for a in price_alerts if a['triggered']]),
            'quiet_hours_enabled': prefs['quiet_hours_enabled'],
            'quiet_hours': f"{prefs['quiet_hours_start']} - {prefs['quiet_hours_end']}"
        }

