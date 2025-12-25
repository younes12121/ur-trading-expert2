"""
Quick test script to verify monitoring integration
"""

import sys
import os

print("=" * 60)
print("🧪 Testing Monitoring Integration")
print("=" * 60)

# Test 1: Check if monitoring modules exist
print("\n1. Checking monitoring modules...")
try:
    from monitoring import get_logger, get_perf_monitor
    print("   ✅ monitoring.py - OK")
except ImportError as e:
    print(f"   ❌ monitoring.py - Missing: {e}")
    sys.exit(1)

# Test 2: Check error messages
print("\n2. Checking error messages...")
try:
    from error_messages import format_error, get_user_friendly_error
    print("   ✅ error_messages.py - OK")
except ImportError as e:
    print(f"   ❌ error_messages.py - Missing: {e}")
    sys.exit(1)

# Test 3: Check support system
print("\n3. Checking support system...")
try:
    from support_system import SupportTicketSystem
    print("   ✅ support_system.py - OK")
except ImportError as e:
    print(f"   ❌ support_system.py - Missing: {e}")
    sys.exit(1)

# Test 4: Check performance optimizer
print("\n4. Checking performance optimizer...")
try:
    from performance_optimizer import get_cache_manager
    print("   ✅ performance_optimizer.py - OK")
except ImportError as e:
    print(f"   ❌ performance_optimizer.py - Missing: {e}")
    sys.exit(1)

# Test 5: Initialize components
print("\n5. Initializing components...")
try:
    logger = get_logger()
    print("   ✅ Logger initialized")
    
    perf_monitor = get_perf_monitor()
    print("   ✅ Performance monitor initialized")
    
    cache = get_cache_manager()
    print("   ✅ Cache manager initialized")
    
    support = SupportTicketSystem()
    print("   ✅ Support system initialized")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")
    sys.exit(1)

# Test 6: Check logs directory
print("\n6. Checking logs directory...")
if not os.path.exists('logs'):
    os.makedirs('logs')
    print("   ✅ Created logs directory")
else:
    print("   ✅ Logs directory exists")

# Test 7: Test logging
print("\n7. Testing logging...")
try:
    logger.log_command('test', 12345, success=True, execution_time=0.1)
    print("   ✅ Command logging works")
    
    logger.log_error(Exception("Test error"), {'test': True})
    print("   ✅ Error logging works")
except Exception as e:
    print(f"   ❌ Logging failed: {e}")
    sys.exit(1)

# Test 8: Test support system
print("\n8. Testing support system...")
try:
    ticket_id = support.create_ticket(
        user_id=999999,
        subject="Test Ticket",
        message="This is a test",
        priority=None  # Will use default
    )
    print(f"   ✅ Support ticket created: #{ticket_id}")
    
    tickets = support.get_user_tickets(999999)
    print(f"   ✅ Retrieved {len(tickets)} ticket(s)")
except Exception as e:
    print(f"   ❌ Support system failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All Tests Passed!")
print("=" * 60)
print("\nMonitoring integration is working correctly!")
print("You can now run: python telegram_bot.py")
print("=" * 60)

