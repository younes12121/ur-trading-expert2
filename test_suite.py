"""
Comprehensive Test Suite for Trading Expert Bot
Tests all commands and features from Phases 7-13
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import bot modules
try:
    from user_manager import UserManager
    from notification_manager import NotificationManager
    from user_profiles import UserProfileManager
    from leaderboard import LeaderboardManager
    from community_features import CommunityManager
    from referral_system import ReferralManager
    from broker_connector import BrokerConnector
    from paper_trading import PaperTrading
    from signal_tracker import SignalTracker
    from educational_assistant import EducationalAssistant
    from ml_predictor import MLSignalPredictor
    from sentiment_analyzer import SentimentAnalyzer
    from order_flow import OrderFlowAnalyzer
    from market_maker import MarketMakerZones
    from smart_money_tracker import SmartMoneyTracker
    from volume_profile import VolumeProfileAnalyzer
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Some modules may not be available. Continuing with available tests...")


class TestResult:
    """Test result container"""
    def __init__(self, test_name: str, passed: bool, message: str = "", error: str = ""):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.error = error
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class TestSuite:
    """Main test suite class"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_user_id = 999999  # Test user ID
        self.test_user_id_2 = 999998  # Second test user
        
    def run_test(self, test_func, test_name: str):
        """Run a single test and record result"""
        try:
            result = test_func()
            if result:
                self.results.append(TestResult(test_name, True, "Test passed"))
                print(f"✅ {test_name}")
                return True
            else:
                self.results.append(TestResult(test_name, False, "Test failed"))
                print(f"❌ {test_name}")
                return False
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            self.results.append(TestResult(test_name, False, "Test crashed", error_msg))
            print(f"💥 {test_name} - ERROR: {error_msg}")
            if "--verbose" in sys.argv:
                print(traceback_str)
            return False
    
    # ============================================================================
    # PHASE 7: EDUCATIONAL ASSISTANT TESTS
    # ============================================================================
    
    def test_educational_assistant_init(self):
        """Test educational assistant initialization"""
        try:
            edu = EducationalAssistant()
            return edu is not None
        except Exception as e:
            if "--verbose" in sys.argv:
                print(f"    Error: {e}")
            return False
    
    def test_get_daily_tip(self):
        """Test daily tip retrieval"""
        try:
            edu = EducationalAssistant()
            tip = edu.get_daily_tip(self.test_user_id)
            return tip is not None and len(tip) > 0
        except:
            return False
    
    def test_get_glossary_term(self):
        """Test glossary term lookup"""
        try:
            edu = EducationalAssistant()
            term = edu.get_glossary_term("RSI")
            return term is not None
        except:
            return False
    
    def test_explain_signal(self):
        """Test signal explanation"""
        try:
            edu = EducationalAssistant()
            explanation = edu.explain_signal("EUR/USD", "BUY")
            return explanation is not None and len(explanation) > 0
        except:
            return False
    
    # ============================================================================
    # PHASE 8: NOTIFICATIONS TESTS
    # ============================================================================
    
    def test_notification_manager_init(self):
        """Test notification manager initialization"""
        try:
            nm = NotificationManager()
            return nm is not None
        except:
            return False
    
    def test_set_price_alert(self):
        """Test price alert creation"""
        try:
            nm = NotificationManager()
            result = nm.set_price_alert(self.test_user_id, "EURUSD", 1.1000, "above")
            return result is not None
        except:
            return False
    
    def test_get_user_preferences(self):
        """Test getting user notification preferences"""
        try:
            nm = NotificationManager()
            prefs = nm.get_user_preferences(self.test_user_id)
            return prefs is not None
        except:
            return False
    
    # ============================================================================
    # PHASE 9: USER TIERS & MONETIZATION TESTS
    # ============================================================================
    
    def test_user_manager_init(self):
        """Test user manager initialization"""
        try:
            um = UserManager()
            return um is not None
        except:
            return False
    
    def test_get_user_tier(self):
        """Test getting user tier"""
        try:
            um = UserManager()
            tier = um.get_user_tier(self.test_user_id)
            return tier in ['free', 'premium', 'vip']
        except:
            return False
    
    def test_has_feature_access(self):
        """Test feature access checking"""
        try:
            um = UserManager()
            # Test free tier access
            has_access = um.has_feature_access(self.test_user_id, 'all_assets')
            return isinstance(has_access, bool)
        except:
            return False
    
    def test_set_user_tier(self):
        """Test setting user tier"""
        try:
            um = UserManager()
            um.set_user_tier(self.test_user_id, 'premium')
            tier = um.get_user_tier(self.test_user_id)
            return tier == 'premium'
        except:
            return False
    
    # ============================================================================
    # PHASE 10: COMMUNITY FEATURES TESTS
    # ============================================================================
    
    def test_user_profiles_init(self):
        """Test user profiles initialization"""
        try:
            upm = UserProfileManager()
            return upm is not None
        except:
            return False
    
    def test_get_profile(self):
        """Test getting user profile"""
        try:
            upm = UserProfileManager()
            profile = upm.get_profile(self.test_user_id)
            return profile is not None
        except:
            return False
    
    def test_follow_user(self):
        """Test following a user"""
        try:
            upm = UserProfileManager()
            result = upm.follow_user(self.test_user_id, self.test_user_id_2)
            return isinstance(result, bool)
        except:
            return False
    
    def test_community_manager_init(self):
        """Test community manager initialization"""
        try:
            cm = CommunityManager()
            return cm is not None
        except:
            return False
    
    def test_enable_copy_trading(self):
        """Test enabling copy trading"""
        try:
            cm = CommunityManager()
            settings = {'lot_multiplier': 1.0, 'max_risk': 2.0}
            result = cm.enable_copy_trading(self.test_user_id, self.test_user_id_2, settings)
            return isinstance(result, bool)
        except:
            return False
    
    def test_get_copy_trading_followers(self):
        """Test getting copy trading followers"""
        try:
            cm = CommunityManager()
            followers = cm.get_copy_trading_followers(self.test_user_id_2)
            return isinstance(followers, list)
        except:
            return False
    
    def test_referral_manager_init(self):
        """Test referral manager initialization"""
        try:
            rm = ReferralManager()
            return rm is not None
        except:
            return False
    
    def test_get_referral_code(self):
        """Test getting referral code"""
        try:
            rm = ReferralManager()
            code = rm.get_referral_code(self.test_user_id)
            return code is not None and len(code) > 0
        except:
            return False
    
    # ============================================================================
    # PHASE 11: BROKER INTEGRATION TESTS
    # ============================================================================
    
    def test_broker_connector_init(self):
        """Test broker connector initialization"""
        try:
            bc = BrokerConnector()
            return bc is not None
        except:
            return False
    
    def test_paper_trading_init(self):
        """Test paper trading initialization"""
        try:
            pt = PaperTrading()
            return pt is not None
        except:
            return False
    
    def test_enable_paper_trading(self):
        """Test enabling paper trading"""
        try:
            pt = PaperTrading()
            result = pt.enable_paper_trading(self.test_user_id, 10000.0)
            return result is True
        except:
            return False
    
    def test_paper_trading_account(self):
        """Test getting paper trading account"""
        try:
            pt = PaperTrading()
            account = pt.get_account(self.test_user_id)
            return account is not None
        except:
            return False
    
    # ============================================================================
    # PHASE 13: AI FEATURES TESTS
    # ============================================================================
    
    def test_ml_predictor_init(self):
        """Test ML predictor initialization"""
        try:
            ml = MLSignalPredictor()
            return ml is not None
        except:
            return False
    
    def test_sentiment_analyzer_init(self):
        """Test sentiment analyzer initialization"""
        try:
            sa = SentimentAnalyzer()
            return sa is not None
        except:
            return False
    
    def test_order_flow_analyzer_init(self):
        """Test order flow analyzer initialization"""
        try:
            ofa = OrderFlowAnalyzer()
            return ofa is not None
        except:
            return False
    
    def test_market_maker_zones_init(self):
        """Test market maker zones initialization"""
        try:
            mmz = MarketMakerZones()
            return mmz is not None
        except:
            return False
    
    def test_smart_money_tracker_init(self):
        """Test smart money tracker initialization"""
        try:
            smt = SmartMoneyTracker()
            return smt is not None
        except:
            return False
    
    def test_volume_profile_analyzer_init(self):
        """Test volume profile analyzer initialization"""
        try:
            vpa = VolumeProfileAnalyzer()
            return vpa is not None
        except:
            return False
    
    # ============================================================================
    # SIGNAL TRACKER TESTS
    # ============================================================================
    
    def test_signal_tracker_init(self):
        """Test signal tracker initialization"""
        try:
            st = SignalTracker()
            return st is not None
        except:
            return False
    
    def test_log_signal(self):
        """Test logging a signal"""
        try:
            st = SignalTracker()
            criteria_details = {
                'passed': ['High confidence', 'Strong trend'],
                'failed': ['Low volume']
            }
            signal_id = st.log_signal(
                "EURUSD", "BUY", 1.1000, 1.1100, 1.0950,
                criteria_passed=18, criteria_total=20,
                criteria_details=criteria_details
            )
            return signal_id > 0
        except:
            return False
    
    def test_get_signal_by_id(self):
        """Test getting signal by ID"""
        try:
            st = SignalTracker()
            # First log a signal
            signal_id = st.log_signal("EURUSD", "BUY", 1.1000, 1.1100, 1.0950)
            # Then retrieve it
            signal = st.get_signal_by_id(signal_id)
            return signal is not None and signal['id'] == signal_id
        except:
            return False
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_user_tier_feature_access(self):
        """Test that tier restrictions work correctly"""
        try:
            um = UserManager()
            # Set to free tier
            um.set_user_tier(self.test_user_id, 'free')
            # Free tier should not have access to all_assets
            has_access = um.has_feature_access(self.test_user_id, 'all_assets')
            return has_access is False
        except:
            return False
    
    def test_copy_trading_notification_flow(self):
        """Test copy trading notification flow"""
        try:
            cm = CommunityManager()
            upm = UserProfileManager()
            
            # Enable copy trading
            settings = {'lot_multiplier': 1.0, 'max_risk': 2.0}
            cm.enable_copy_trading(self.test_user_id, self.test_user_id_2, settings)
            
            # Check followers
            followers = cm.get_copy_trading_followers(self.test_user_id_2)
            return self.test_user_id in followers
        except:
            return False
    
    # ============================================================================
    # RUN ALL TESTS
    # ============================================================================
    
    def run_all_tests(self, quick_mode=False):
        """Run all test suites
        
        Args:
            quick_mode: If True, skip slow tests
        """
        print("Starting Comprehensive Test Suite...\n")
        print("=" * 60)
        
        if quick_mode:
            print("⚡ Quick Mode: Skipping slow tests\n")
        
        # Phase 7: Educational Assistant
        print("\n📚 Phase 7: Educational Assistant")
        print("-" * 60)
        self.run_test(self.test_educational_assistant_init, "Educational Assistant Init")
        self.run_test(self.test_get_daily_tip, "Get Daily Tip")
        self.run_test(self.test_get_glossary_term, "Get Glossary Term")
        self.run_test(self.test_explain_signal, "Explain Signal")
        
        # Phase 8: Notifications
        print("\n🔔 Phase 8: Smart Notifications")
        print("-" * 60)
        self.run_test(self.test_notification_manager_init, "Notification Manager Init")
        self.run_test(self.test_set_price_alert, "Set Price Alert")
        self.run_test(self.test_get_user_preferences, "Get User Preferences")
        
        # Phase 9: User Tiers
        print("\n💳 Phase 9: User Tiers & Monetization")
        print("-" * 60)
        self.run_test(self.test_user_manager_init, "User Manager Init")
        self.run_test(self.test_get_user_tier, "Get User Tier")
        self.run_test(self.test_has_feature_access, "Check Feature Access")
        self.run_test(self.test_set_user_tier, "Set User Tier")
        
        # Phase 10: Community Features
        print("\n👥 Phase 10: Community Features")
        print("-" * 60)
        self.run_test(self.test_user_profiles_init, "User Profiles Init")
        self.run_test(self.test_get_profile, "Get Profile")
        self.run_test(self.test_follow_user, "Follow User")
        self.run_test(self.test_community_manager_init, "Community Manager Init")
        self.run_test(self.test_enable_copy_trading, "Enable Copy Trading")
        self.run_test(self.test_get_copy_trading_followers, "Get Copy Trading Followers")
        self.run_test(self.test_referral_manager_init, "Referral Manager Init")
        self.run_test(self.test_get_referral_code, "Get Referral Code")
        
        # Phase 11: Broker Integration
        print("\n🔌 Phase 11: Broker Integration")
        print("-" * 60)
        self.run_test(self.test_broker_connector_init, "Broker Connector Init")
        self.run_test(self.test_paper_trading_init, "Paper Trading Init")
        self.run_test(self.test_enable_paper_trading, "Enable Paper Trading")
        self.run_test(self.test_paper_trading_account, "Get Paper Trading Account")
        
        # Phase 13: AI Features
        print("\n🤖 Phase 13: Advanced AI Features")
        print("-" * 60)
        self.run_test(self.test_ml_predictor_init, "ML Predictor Init")
        self.run_test(self.test_sentiment_analyzer_init, "Sentiment Analyzer Init")
        self.run_test(self.test_order_flow_analyzer_init, "Order Flow Analyzer Init")
        self.run_test(self.test_market_maker_zones_init, "Market Maker Zones Init")
        self.run_test(self.test_smart_money_tracker_init, "Smart Money Tracker Init")
        self.run_test(self.test_volume_profile_analyzer_init, "Volume Profile Analyzer Init")
        
        # Signal Tracker
        print("\n📊 Signal Tracker")
        print("-" * 60)
        self.run_test(self.test_signal_tracker_init, "Signal Tracker Init")
        self.run_test(self.test_log_signal, "Log Signal")
        self.run_test(self.test_get_signal_by_id, "Get Signal By ID")
        
        # Integration Tests
        print("\n🔗 Integration Tests")
        print("-" * 60)
        self.run_test(self.test_user_tier_feature_access, "Tier Feature Access")
        self.run_test(self.test_copy_trading_notification_flow, "Copy Trading Flow")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.test_name}")
                    if result.error:
                        print(f"    Error: {result.error}")
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to JSON file"""
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'results': [
                {
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'message': r.message,
                    'error': r.error,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ]
        }
        
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run Trading Bot Test Suite')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--verbose', action='store_true', help='Show detailed error messages')
    args = parser.parse_args()
    
    suite = TestSuite()
    suite.run_all_tests(quick_mode=args.quick)

