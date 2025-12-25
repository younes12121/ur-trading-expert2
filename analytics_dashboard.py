"""
Analytics Dashboard Module
Tracks key business metrics: DAU, MAU, conversion rates, churn, LTV, CAC, MRR
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Comprehensive analytics tracking for business metrics"""
    
    def __init__(self, database_manager=None):
        self.db = database_manager
        self.metrics_cache = {}
        
    def get_daily_active_users(self, date: datetime = None) -> int:
        """Get Daily Active Users (DAU)"""
        if date is None:
            date = datetime.now()
        
        # In production, query database
        # For now, return cached or simulated data
        cache_key = f"dau_{date.strftime('%Y-%m-%d')}"
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]
        
        # Simulated - replace with actual database query
        dau = 150  # Example
        self.metrics_cache[cache_key] = dau
        return dau
    
    def get_monthly_active_users(self, month: datetime = None) -> int:
        """Get Monthly Active Users (MAU)"""
        if month is None:
            month = datetime.now().replace(day=1)
        
        cache_key = f"mau_{month.strftime('%Y-%m')}"
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]
        
        # Simulated - replace with actual database query
        mau = 2000  # Example
        self.metrics_cache[cache_key] = mau
        return mau
    
    def get_conversion_rates(self, period_days: int = 30) -> Dict[str, float]:
        """Get conversion rates for different tiers"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Simulated data - replace with actual queries
        conversions = {
            'free_to_premium': 0.25,  # 25%
            'premium_to_vip': 0.10,   # 10%
            'free_to_vip': 0.02,      # 2%
            'trial_to_premium': 0.60, # 60%
            'overall_conversion': 0.27 # 27%
        }
        
        return conversions
    
    def get_churn_rate(self, period_days: int = 30) -> Dict[str, float]:
        """Calculate churn rate by tier"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Simulated - replace with actual calculation
        churn = {
            'free': 0.15,      # 15% monthly churn
            'premium': 0.05,   # 5% monthly churn
            'vip': 0.03,       # 3% monthly churn
            'overall': 0.08    # 8% overall
        }
        
        return churn
    
    def get_customer_lifetime_value(self, tier: str = 'premium') -> Dict[str, float]:
        """Calculate Customer Lifetime Value (LTV)"""
        # LTV = Average Revenue Per User (ARPU) × Gross Margin × (1 / Churn Rate)
        
        arpu = {
            'premium': 29.00,
            'vip': 99.00
        }
        
        gross_margin = 0.85  # 85% (after Stripe fees, infrastructure)
        churn_rates = self.get_churn_rate()
        
        ltv = {}
        for t in ['premium', 'vip']:
            churn = churn_rates.get(t, 0.05)
            avg_lifetime_months = 1 / churn if churn > 0 else 12
            ltv[t] = arpu[t] * gross_margin * avg_lifetime_months
        
        return ltv
    
    def get_customer_acquisition_cost(self, period_days: int = 30) -> Dict[str, float]:
        """Calculate Customer Acquisition Cost (CAC)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Simulated marketing spend
        marketing_spend = {
            'paid_ads': 1000.00,
            'content_creation': 500.00,
            'influencer': 300.00,
            'tools': 200.00,
            'total': 2000.00
        }
        
        # Simulated new customers acquired
        new_customers = {
            'free': 100,
            'premium': 25,
            'vip': 5,
            'total_paid': 30
        }
        
        cac = {
            'premium': marketing_spend['total'] / new_customers['premium'] if new_customers['premium'] > 0 else 0,
            'vip': marketing_spend['total'] / new_customers['vip'] if new_customers['vip'] > 0 else 0,
            'overall': marketing_spend['total'] / new_customers['total_paid'] if new_customers['total_paid'] > 0 else 0
        }
        
        return cac
    
    def get_monthly_recurring_revenue(self, month: datetime = None) -> Dict[str, float]:
        """Calculate Monthly Recurring Revenue (MRR)"""
        if month is None:
            month = datetime.now().replace(day=1)
        
        # Simulated subscription counts
        subscriptions = {
            'premium': 250,
            'vip': 50
        }
        
        pricing = {
            'premium': 29.00,
            'vip': 99.00
        }
        
        mrr = {
            'premium': subscriptions['premium'] * pricing['premium'],
            'vip': subscriptions['vip'] * pricing['vip'],
            'total': (subscriptions['premium'] * pricing['premium']) + 
                     (subscriptions['vip'] * pricing['vip'])
        }
        
        return mrr
    
    def get_net_promoter_score(self) -> Dict[str, float]:
        """Calculate Net Promoter Score (NPS)"""
        # NPS = % Promoters - % Detractors
        # Promoters: 9-10, Passives: 7-8, Detractors: 0-6
        
        # Simulated survey responses
        responses = {
            'promoters': 60,   # 9-10 rating
            'passives': 30,    # 7-8 rating
            'detractors': 10,  # 0-6 rating
            'total': 100
        }
        
        promoter_pct = (responses['promoters'] / responses['total']) * 100
        detractor_pct = (responses['detractors'] / responses['total']) * 100
        
        nps = promoter_pct - detractor_pct
        
        return {
            'nps': nps,
            'promoters_pct': promoter_pct,
            'passives_pct': (responses['passives'] / responses['total']) * 100,
            'detractors_pct': detractor_pct,
            'total_responses': responses['total']
        }
    
    def get_user_growth_metrics(self, period_days: int = 30) -> Dict[str, any]:
        """Get user growth metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Simulated growth data
        growth = {
            'new_users': 150,
            'new_premium': 25,
            'new_vip': 5,
            'growth_rate': 0.08,  # 8% monthly growth
            'retention_rate': 0.92,  # 92% retention
            'activation_rate': 0.75   # 75% of new users activate
        }
        
        return growth
    
    def get_revenue_metrics(self, period_days: int = 30) -> Dict[str, float]:
        """Get comprehensive revenue metrics"""
        mrr = self.get_monthly_recurring_revenue()
        ltv = self.get_customer_lifetime_value()
        cac = self.get_customer_acquisition_cost(period_days)
        
        # Calculate LTV:CAC ratio
        ltv_cac_ratio = {
            'premium': ltv['premium'] / cac['premium'] if cac['premium'] > 0 else 0,
            'vip': ltv['vip'] / cac['vip'] if cac['vip'] > 0 else 0
        }
        
        # Annual Run Rate (ARR)
        arr = mrr['total'] * 12
        
        return {
            'mrr': mrr,
            'arr': arr,
            'ltv': ltv,
            'cac': cac,
            'ltv_cac_ratio': ltv_cac_ratio,
            'gross_margin': 0.85,
            'net_margin': 0.65
        }
    
    def generate_dashboard_report(self) -> Dict[str, any]:
        """Generate comprehensive dashboard report"""
        logger.info("Generating analytics dashboard report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': 'last_30_days',
            'user_metrics': {
                'dau': self.get_daily_active_users(),
                'mau': self.get_monthly_active_users(),
                'growth': self.get_user_growth_metrics()
            },
            'conversion_metrics': {
                'conversion_rates': self.get_conversion_rates(),
                'churn_rates': self.get_churn_rate()
            },
            'revenue_metrics': self.get_revenue_metrics(),
            'engagement_metrics': {
                'nps': self.get_net_promoter_score(),
                'avg_session_duration': 15.5,  # minutes
                'commands_per_user_per_day': 5.2,
                'signals_viewed_per_user': 12.3
            },
            'tier_distribution': {
                'free': 7000,
                'premium': 2500,
                'vip': 500,
                'total': 10000
            }
        }
        
        return report
    
    def print_dashboard_summary(self, report: Dict = None):
        """Print human-readable dashboard summary"""
        if report is None:
            report = self.generate_dashboard_report()
        
        print("=" * 70)
        print("📊 ANALYTICS DASHBOARD - BUSINESS METRICS")
        print("=" * 70)
        print(f"Report Date: {report['timestamp']}")
        print(f"Period: {report['period']}")
        print()
        
        # User Metrics
        user_metrics = report['user_metrics']
        print("👥 USER METRICS")
        print("-" * 70)
        print(f"Daily Active Users (DAU): {user_metrics['dau']:,}")
        print(f"Monthly Active Users (MAU): {user_metrics['mau']:,}")
        print(f"Growth Rate: {user_metrics['growth']['growth_rate']*100:.1f}%")
        print(f"Retention Rate: {user_metrics['growth']['retention_rate']*100:.1f}%")
        print()
        
        # Conversion Metrics
        conv_metrics = report['conversion_metrics']
        print("📈 CONVERSION METRICS")
        print("-" * 70)
        print(f"Free → Premium: {conv_metrics['conversion_rates']['free_to_premium']*100:.1f}%")
        print(f"Premium → VIP: {conv_metrics['conversion_rates']['premium_to_vip']*100:.1f}%")
        print(f"Overall Conversion: {conv_metrics['conversion_rates']['overall_conversion']*100:.1f}%")
        print(f"Overall Churn: {conv_metrics['churn_rates']['overall']*100:.1f}%")
        print()
        
        # Revenue Metrics
        rev_metrics = report['revenue_metrics']
        print("💰 REVENUE METRICS")
        print("-" * 70)
        print(f"Monthly Recurring Revenue (MRR): ${rev_metrics['mrr']['total']:,.2f}")
        print(f"Annual Run Rate (ARR): ${rev_metrics['arr']:,.2f}")
        print(f"Premium LTV: ${rev_metrics['ltv']['premium']:,.2f}")
        print(f"VIP LTV: ${rev_metrics['ltv']['vip']:,.2f}")
        print(f"Premium CAC: ${rev_metrics['cac']['premium']:,.2f}")
        print(f"VIP CAC: ${rev_metrics['cac']['vip']:,.2f}")
        print(f"Premium LTV:CAC Ratio: {rev_metrics['ltv_cac_ratio']['premium']:.2f}:1")
        print(f"VIP LTV:CAC Ratio: {rev_metrics['ltv_cac_ratio']['vip']:.2f}:1")
        print()
        
        # Engagement Metrics
        eng_metrics = report['engagement_metrics']
        print("🎯 ENGAGEMENT METRICS")
        print("-" * 70)
        print(f"Net Promoter Score (NPS): {eng_metrics['nps']['nps']:.1f}")
        print(f"Avg Session Duration: {eng_metrics['avg_session_duration']:.1f} minutes")
        print(f"Commands per User/Day: {eng_metrics['commands_per_user_per_day']:.1f}")
        print()
        
        # Tier Distribution
        tiers = report['tier_distribution']
        print("👤 TIER DISTRIBUTION")
        print("-" * 70)
        print(f"Free: {tiers['free']:,} ({tiers['free']/tiers['total']*100:.1f}%)")
        print(f"Premium: {tiers['premium']:,} ({tiers['premium']/tiers['total']*100:.1f}%)")
        print(f"VIP: {tiers['vip']:,} ({tiers['vip']/tiers['total']*100:.1f}%)")
        print(f"Total: {tiers['total']:,}")
        print()
        print("=" * 70)

def main():
    """Test analytics dashboard"""
    dashboard = AnalyticsDashboard()
    report = dashboard.generate_dashboard_report()
    dashboard.print_dashboard_summary(report)
    
    # Save report
    with open('analytics_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Analytics report saved to: analytics_report.json")

if __name__ == "__main__":
    main()

