"""
Test PostgreSQL Database Connection
Run this to verify your DATABASE_URL is correct before migration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if DATABASE_URL is set
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("❌ ERROR: DATABASE_URL not set in .env file")
    print("\n📝 To fix:")
    print("1. Create .env file (copy from ENV_TEMPLATE.txt)")
    print("2. Add: DATABASE_URL=postgresql://user:password@host:port/database")
    print("3. Replace with your actual PostgreSQL connection string")
    sys.exit(1)

# Check if it's PostgreSQL (not SQLite)
if 'postgresql' not in db_url.lower() and 'postgres' not in db_url.lower():
    print("⚠️  WARNING: DATABASE_URL doesn't look like PostgreSQL")
    print(f"   Current: {db_url[:50]}...")
    print("   Expected format: postgresql://user:password@host:port/database")
    response = input("\nContinue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

print(f"🔗 Connecting to database...")
print(f"   Connection string: {db_url[:50]}...")

try:
    from database import DatabaseManager
    
    # Try to connect
    db = DatabaseManager(db_url)
    
    # Create tables (if they don't exist)
    print("\n📦 Creating database tables...")
    db.create_tables()
    
    # Test query
    session = db.get_session()
    from database import User
    
    user_count = session.query(User).count()
    session.close()
    
    print("✅ Database connection successful!")
    print("✅ Tables created/verified successfully!")
    print(f"✅ Current users in database: {user_count}")
    
    if user_count == 0:
        print("\n💡 Database is empty - ready for migration!")
        print("   Run: python migrate_to_postgresql.py --dry-run")
    else:
        print(f"\n💡 Database has {user_count} users already")
        print("   Migration may skip existing users")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📦 Install dependencies:")
    print("   pip install psycopg2-binary sqlalchemy python-dotenv")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n🔍 Troubleshooting:")
    print("1. Verify DATABASE_URL is correct in .env file")
    print("2. Check PostgreSQL is running (for local)")
    print("3. Verify credentials are correct")
    print("4. Check firewall settings (for cloud)")
    print("5. Verify database exists")
    sys.exit(1)

print("\n✅ Ready for migration!")
print("   Next step: python migrate_to_postgresql.py --dry-run")

