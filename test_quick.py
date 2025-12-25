"""
Quick Test Suite - Fast validation of core functionality
Runs essential tests only (no slow operations)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing Module Imports...")
    print("-" * 60)
    
    modules = [
        'user_manager',
        'notification_manager',
        'user_profiles',
        'leaderboard',
        'community_features',
        'referral_system',
        'broker_connector',
        'paper_trading',
        'signal_tracker',
        'educational_assistant',
        'ml_predictor',
        'sentiment_analyzer',
        'order_flow',
        'market_maker',
        'smart_money_tracker',
        'volume_profile',
    ]
    
    results = {}
    for module_name in modules:
        try:
            __import__(module_name)
            results[module_name] = True
            print(f"[OK] {module_name}")
        except ImportError as e:
            results[module_name] = False
            print(f"[FAIL] {module_name} - {e}")
        except Exception as e:
            results[module_name] = False
            print(f"[ERROR] {module_name} - {e}")
    
    print("\n" + "-" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Import Test: {passed}/{total} modules imported successfully")

    return results


def test_initialization():
    """Test that modules can be initialized"""
    print("\nTesting Module Initialization...")
    print("-" * 60)
    
    results = {}
    
    # Test each module
    try:
        from user_manager import UserManager
        um = UserManager()
        results['user_manager'] = um is not None
        print(f"{'[OK]' if results['user_manager'] else '[FAIL]'} user_manager")
    except Exception as e:
        results['user_manager'] = False
        print(f"[FAIL] user_manager - {e}")

    try:
        from notification_manager import NotificationManager
        nm = NotificationManager()
        results['notification_manager'] = nm is not None
        print(f"{'[OK]' if results['notification_manager'] else '[FAIL]'} notification_manager")
    except Exception as e:
        results['notification_manager'] = False
        print(f"[FAIL] notification_manager - {e}")

    try:
        from user_profiles import UserProfileManager
        upm = UserProfileManager()
        results['user_profiles'] = upm is not None
        print(f"{'[OK]' if results['user_profiles'] else '[FAIL]'} user_profiles")
    except Exception as e:
        results['user_profiles'] = False
        print(f"[FAIL] user_profiles - {e}")

    try:
        from signal_tracker import SignalTracker
        st = SignalTracker()
        results['signal_tracker'] = st is not None
        print(f"{'[OK]' if results['signal_tracker'] else '[FAIL]'} signal_tracker")
    except Exception as e:
        results['signal_tracker'] = False
        print(f"[FAIL] signal_tracker - {e}")

    try:
        from paper_trading import PaperTrading
        pt = PaperTrading()
        results['paper_trading'] = pt is not None
        print(f"{'[OK]' if results['paper_trading'] else '[FAIL]'} paper_trading")
    except Exception as e:
        results['paper_trading'] = False
        print(f"[FAIL] paper_trading - {e}")
    
    print("\n" + "-" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Initialization Test: {passed}/{total} modules initialized successfully")
    
    return results


def test_basic_functionality():
    """Test basic functionality of key modules"""
    print("\nTesting Basic Functionality...")
    print("-" * 60)
    
    results = {}
    test_user_id = 999999
    
    # Test User Manager
    try:
        from user_manager import UserManager
        um = UserManager()
        tier = um.get_user_tier(test_user_id)
        results['user_tier'] = tier in ['free', 'premium', 'vip']
        print(f"{'[OK]' if results['user_tier'] else '[FAIL]'} User tier retrieval")
    except Exception as e:
        results['user_tier'] = False
        print(f"[FAIL] User tier - {e}")

    # Test Signal Tracker
    try:
        from signal_tracker import SignalTracker
        st = SignalTracker()
        signal_id = st.log_signal("EURUSD", "BUY", 1.1000, 1.1100, 1.0950)
        signal = st.get_signal_by_id(signal_id)
        results['signal_tracking'] = signal is not None and signal['id'] == signal_id
        print(f"{'[OK]' if results['signal_tracking'] else '[FAIL]'} Signal tracking")
    except Exception as e:
        results['signal_tracking'] = False
        print(f"[FAIL] Signal tracking - {e}")

    # Test Paper Trading
    try:
        from paper_trading import PaperTrading
        pt = PaperTrading()
        pt.enable_paper_trading(test_user_id, 10000.0)
        account = pt.get_account(test_user_id)
        results['paper_trading'] = account is not None and account.get('enabled')
        print(f"{'[OK]' if results['paper_trading'] else '[FAIL]'} Paper trading")
    except Exception as e:
        results['paper_trading'] = False
        print(f"[FAIL] Paper trading - {e}")
    
    print("\n" + "-" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Functionality Test: {passed}/{total} features working")
    
    return results


def main():
    """Run quick tests"""
    print("=" * 60)
    print("QUICK TEST SUITE")
    print("=" * 60)
    print("Fast validation of core functionality\n")
    
    import_results = test_imports()
    init_results = test_initialization()
    func_results = test_basic_functionality()
    
    print("\n" + "=" * 60)
    print("QUICK TEST SUMMARY")
    print("=" * 60)
    
    total_imports = len(import_results)
    passed_imports = sum(1 for v in import_results.values() if v)
    
    total_init = len(init_results)
    passed_init = sum(1 for v in init_results.values() if v)
    
    total_func = len(func_results)
    passed_func = sum(1 for v in func_results.values() if v)
    
    print(f"\nImports: {passed_imports}/{total_imports} [OK]")
    print(f"Initialization: {passed_init}/{total_init} [OK]")
    print(f"Functionality: {passed_func}/{total_func} [OK]")

    overall_passed = passed_imports + passed_init + passed_func
    overall_total = total_imports + total_init + total_func

    print(f"\nOverall: {overall_passed}/{overall_total} tests passed")
    print(f"Success Rate: {(overall_passed/overall_total*100):.1f}%")

    if overall_passed == overall_total:
        print("\n[SUCCESS] All quick tests passed!")
    else:
        print(f"\n[WARNING] {overall_total - overall_passed} tests failed. Review output above.")


if __name__ == "__main__":
    main()



