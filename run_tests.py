"""
Main test runner script
Runs all test suites and generates report
"""

import sys
import os
import subprocess
from datetime import datetime

def run_test_suite():
    """Run the main test suite"""
    print("=" * 70)
    print("TRADING EXPERT BOT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    original_dir = os.getcwd()
    try:
        os.chdir(script_dir)
        
        # Check if quick mode requested
        quick_mode = '--quick' in sys.argv or '-q' in sys.argv
        
        if quick_mode:
            print("Running Quick Tests...")
            print("-" * 70)
            from test_quick import main as quick_main
            quick_main()
        else:
            # Run full test suite
            print("Running Full Test Suite...")
            print("-" * 70)
            from test_suite import TestSuite
            suite = TestSuite()
            suite.run_all_tests(quick_mode=False)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Tests interrupted by user")
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure you're running from the correct directory.")
    except Exception as e:
        print(f"[ERROR] Error running test suite: {e}")
        import traceback
        traceback.print_exc()
    finally:
        os.chdir(original_dir)

    print("\n" + "=" * 70)
    print("[COMPLETE] Test Suite Complete")
    print("=" * 70)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("\nNext Steps:")
    print("1. Review test results above")
    print("2. Check test_results_*.json for detailed results")
    print("3. Fix any failing tests")
    print("4. Run manual testing using QA_CHECKLIST.md")
    print("5. Perform integration testing with real Telegram bot")


if __name__ == "__main__":
    run_test_suite()

