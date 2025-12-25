"""
Upgrade Analytics Dashboard
Provides comprehensive analytics for upgrade path performance
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class UpgradeAnalyticsDashboard:
    """Analytics dashboard for upgrade path performance"""
    
    def __init__(self, upgrade_tracking_file="upgrade_tracking.json", users_file="users_data.json"):
        self.upgrade_tracking_file = upgrade_tracking_file
        self.users_file = users_file
        self.load_data()
    
    def load_data(self):
        """Load tracking and user data"""
        # Load upgrade tracking
        if os.path.exists(self.upgrade_tracking_file):
            try:
                with open(self.upgrade_tracking_file, 'r') as f:
                    self.upgrade_data = json.load(f)
            except:
                self.upgrade_data = {}
        else:
            self.upgrade_data = {}
        
        # Load user data
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users_data = json.load(f)
            except:
                self.users_data = {}
        else:
            self.users_data = {}
    
    def get_conversion_funnel(self) -> Dict:
        """Get conversion funnel metrics"""
        total_users = len(self.upgrade_data)
        if total_users == 0:
            return {
                'total_users': 0,
                'free_users': 0,
                'premium_users': 0,
                'vip_users': 0,
                'trials_started': 0,
                'conversion_rates': {}
            }
        
        # Count users by tier
        free_count = 0
        premium_count = 0
        vip_count = 0
        trials_started = 0
        
        for user_id, user_data in self.users_data.items():
            tier = user_data.get('tier', 'free')
            if tier == 'free':
                free_count += 1
            elif tier == 'premium':
                premium_count += 1
            elif tier == 'vip':
                vip_count += 1
        
        # Count trials
        for user_id, tracking in self.upgrade_data.items():
            if tracking.get('trial_started', False):
                trials_started += 1
        
        # Calculate conversion rates
        free_to_premium_rate = (premium_count / free_count * 100) if free_count > 0 else 0
        premium_to_vip_rate = (vip_count / premium_count * 100) if premium_count > 0 else 0
        trial_to_paid_rate = (premium_count / trials_started * 100) if trials_started > 0 else 0
        
        return {
            'total_users': total_users,
            'free_users': free_count,
            'premium_users': premium_count,
            'vip_users': vip_count,
            'trials_started': trials_started,
            'conversion_rates': {
                'free_to_premium': round(free_to_premium_rate, 2),
                'premium_to_vip': round(premium_to_vip_rate, 2),
                'trial_to_paid': round(trial_to_paid_rate, 2)
            }
        }
    
    def get_trigger_performance(self) -> Dict:
        """Get performance metrics for each trigger type"""
        trigger_stats = defaultdict(lambda: {
            'shown': 0,
            'converted': 0,
            'dismissed': 0,
            'conversion_rate': 0.0
        })
        
        for user_id, tracking in self.upgrade_data.items():
            events = tracking.get('conversion_events', [])
            prompts_shown = tracking.get('upgrade_prompts_shown', 0)
            
            # Count trigger types shown (from prompts_shown)
            if prompts_shown > 0:
                # We can't determine exact trigger type from current data
                # But we can track overall performance
                pass
            
            # Count conversions
            for event in events:
                if event['type'] == 'trial_started':
                    trigger_stats['trial_started']['converted'] += 1
                elif event['type'] == 'upgrade_dismissed':
                    trigger_stats['all']['dismissed'] += 1
        
        # Calculate conversion rates
        for trigger, stats in trigger_stats.items():
            if stats['shown'] > 0:
                stats['conversion_rate'] = round((stats['converted'] / stats['shown']) * 100, 2)
        
        return dict(trigger_stats)
    
    def get_engagement_metrics(self) -> Dict:
        """Get user engagement metrics"""
        engagement_scores = []
        commands_per_user = []
        days_active = []
        
        for user_id, tracking in self.upgrade_data.items():
            engagement_scores.append(tracking.get('engagement_score', 0))
            commands_per_user.append(tracking.get('commands_today', 0))
            
            try:
                signup = datetime.strptime(tracking.get('signup_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                days = (datetime.now() - signup).days
                days_active.append(days)
            except:
                days_active.append(0)
        
        if not engagement_scores:
            return {
                'avg_engagement': 0,
                'high_engagement_users': 0,
                'avg_commands_per_user': 0,
                'avg_days_active': 0
            }
        
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        high_engagement = sum(1 for score in engagement_scores if score > 50)
        avg_commands = sum(commands_per_user) / len(commands_per_user) if commands_per_user else 0
        avg_days = sum(days_active) / len(days_active) if days_active else 0
        
        return {
            'avg_engagement': round(avg_engagement, 2),
            'high_engagement_users': high_engagement,
            'high_engagement_rate': round((high_engagement / len(engagement_scores)) * 100, 2) if engagement_scores else 0,
            'avg_commands_per_user': round(avg_commands, 2),
            'avg_days_active': round(avg_days, 2)
        }
    
    def get_revenue_metrics(self) -> Dict:
        """Get revenue metrics"""
        premium_count = sum(1 for u in self.users_data.values() if u.get('tier') == 'premium')
        vip_count = sum(1 for u in self.users_data.values() if u.get('tier') == 'vip')
        
        # Pricing (from UPDATED_PRICING_STRUCTURE.md)
        premium_price = 39.00
        vip_price = 129.00
        
        mrr = (premium_count * premium_price) + (vip_count * vip_price)
        arr = mrr * 12
        
        return {
            'premium_subscribers': premium_count,
            'vip_subscribers': vip_count,
            'monthly_recurring_revenue': round(mrr, 2),
            'annual_recurring_revenue': round(arr, 2),
            'avg_revenue_per_user': round(mrr / len(self.users_data), 2) if self.users_data else 0
        }
    
    def get_time_series_data(self, days: int = 30) -> Dict:
        """Get time series data for trends"""
        # Group events by date
        daily_events = defaultdict(lambda: {
            'signups': 0,
            'trials_started': 0,
            'upgrades': 0,
            'commands': 0
        })
        
        for user_id, tracking in self.upgrade_data.items():
            # Signup date
            try:
                signup_date = tracking.get('signup_date', datetime.now().strftime('%Y-%m-%d'))
                if signup_date:
                    daily_events[signup_date]['signups'] += 1
            except:
                pass
            
            # Events
            for event in tracking.get('conversion_events', []):
                try:
                    event_date = event['timestamp'].split(' ')[0]
                    if event['type'] == 'trial_started':
                        daily_events[event_date]['trials_started'] += 1
                    elif event['type'] == 'subscription_completed':
                        daily_events[event_date]['upgrades'] += 1
                except:
                    pass
        
        return dict(daily_events)
    
    def generate_dashboard_report(self) -> str:
        """Generate comprehensive dashboard report"""
        funnel = self.get_conversion_funnel()
        engagement = self.get_engagement_metrics()
        revenue = self.get_revenue_metrics()
        triggers = self.get_trigger_performance()
        
        report = "📊 *UPGRADE ANALYTICS DASHBOARD*\n\n"
        report += "=" * 50 + "\n\n"
        
        # Conversion Funnel
        report += "🎯 *CONVERSION FUNNEL*\n"
        report += f"Total Users: {funnel['total_users']}\n"
        report += f"Free: {funnel['free_users']} ({round(funnel['free_users']/funnel['total_users']*100, 1)}%)\n" if funnel['total_users'] > 0 else "Free: 0\n"
        report += f"Premium: {funnel['premium_users']} ({round(funnel['premium_users']/funnel['total_users']*100, 1)}%)\n" if funnel['total_users'] > 0 else "Premium: 0\n"
        report += f"VIP: {funnel['vip_users']} ({round(funnel['vip_users']/funnel['total_users']*100, 1)}%)\n" if funnel['total_users'] > 0 else "VIP: 0\n"
        report += f"Trials Started: {funnel['trials_started']}\n\n"
        
        report += "*Conversion Rates:*\n"
        report += f"Free → Premium: {funnel['conversion_rates']['free_to_premium']}%\n"
        report += f"Premium → VIP: {funnel['conversion_rates']['premium_to_vip']}%\n"
        report += f"Trial → Paid: {funnel['conversion_rates']['trial_to_paid']}%\n\n"
        
        # Engagement Metrics
        report += "🔥 *ENGAGEMENT METRICS*\n"
        report += f"Avg Engagement Score: {engagement['avg_engagement']}/100\n"
        report += f"High Engagement Users: {engagement['high_engagement_users']} ({engagement['high_engagement_rate']}%)\n"
        report += f"Avg Commands/User: {engagement['avg_commands_per_user']}\n"
        report += f"Avg Days Active: {engagement['avg_days_active']}\n\n"
        
        # Revenue Metrics
        report += "💰 *REVENUE METRICS*\n"
        report += f"Premium Subscribers: {revenue['premium_subscribers']}\n"
        report += f"VIP Subscribers: {revenue['vip_subscribers']}\n"
        report += f"Monthly Recurring Revenue: ${revenue['monthly_recurring_revenue']:,.2f}\n"
        report += f"Annual Recurring Revenue: ${revenue['annual_recurring_revenue']:,.2f}\n"
        report += f"Avg Revenue Per User: ${revenue['avg_revenue_per_user']:.2f}\n\n"
        
        # Trigger Performance
        report += "🎯 *TRIGGER PERFORMANCE*\n"
        if triggers:
            for trigger, stats in triggers.items():
                report += f"{trigger}:\n"
                report += f"  Shown: {stats['shown']}\n"
                report += f"  Converted: {stats['converted']}\n"
                report += f"  Conversion Rate: {stats['conversion_rate']}%\n"
        else:
            report += "No trigger data available yet.\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def get_top_performing_triggers(self, limit: int = 5) -> List[Dict]:
        """Get top performing triggers by conversion rate"""
        triggers = self.get_trigger_performance()
        
        # Sort by conversion rate
        sorted_triggers = sorted(
            triggers.items(),
            key=lambda x: x[1]['conversion_rate'],
            reverse=True
        )
        
        return [
            {
                'trigger': trigger,
                'stats': stats
            }
            for trigger, stats in sorted_triggers[:limit]
        ]


# Global instance
_dashboard = None

def get_dashboard() -> UpgradeAnalyticsDashboard:
    """Get global dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = UpgradeAnalyticsDashboard()
    return _dashboard
