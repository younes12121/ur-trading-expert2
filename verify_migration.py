"""
Verify Database Migration
Run this after migration to verify all data was migrated correctly
"""

import os
from dotenv import load_dotenv
from database import DatabaseManager, User, Trade, Signal, UserNotification

load_dotenv()

db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("❌ ERROR: DATABASE_URL not set in .env file")
    exit(1)

print("🔍 Verifying database migration...")
print(f"   Connection: {db_url[:50]}...\n")

try:
    db = DatabaseManager(db_url)
    session = db.get_session()
    
    # Count records
    user_count = session.query(User).count()
    trade_count = session.query(Trade).count()
    signal_count = session.query(Signal).count()
    notification_count = session.query(UserNotification).count()
    
    print("📊 Database Statistics:")
    print(f"   Users: {user_count}")
    print(f"   Trades: {trade_count}")
    print(f"   Signals: {signal_count}")
    print(f"   Notifications: {notification_count}")
    
    # Show sample data
    if user_count > 0:
        print("\n👤 Sample Users:")
        users = session.query(User).limit(5).all()
        for user in users:
            print(f"   - Telegram ID: {user.telegram_id}, Tier: {user.tier.value}, Created: {user.created_at}")
    else:
        print("\n⚠️  No users found in database")
    
    if trade_count > 0:
        print(f"\n💼 Trades: {trade_count} total")
        trades = session.query(Trade).limit(3).all()
        for trade in trades:
            print(f"   - {trade.asset} {trade.direction.value} @ {trade.entry}")
    else:
        print("\n💼 No trades found in database")
    
    if signal_count > 0:
        print(f"\n📡 Signals: {signal_count} total")
        signals = session.query(Signal).limit(3).all()
        for signal in signals:
            print(f"   - {signal.pair} {signal.direction.value} @ {signal.entry}")
    else:
        print("\n📡 No signals found in database")
    
    # Check for errors
    print("\n✅ Migration verification complete!")
    
    if user_count == 0 and trade_count == 0 and signal_count == 0:
        print("\n⚠️  WARNING: Database appears empty")
        print("   This could mean:")
        print("   1. Migration hasn't run yet")
        print("   2. JSON files were empty")
        print("   3. Migration failed silently")
        print("\n   Check migration logs for details")
    
    session.close()
    
except Exception as e:
    print(f"❌ Error verifying migration: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

