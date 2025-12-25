"""
Database Migration Quick Start
Interactive script to guide you through the migration process
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file exists")
        return True
    else:
        print("❌ .env file not found")
        print("\n📝 To create .env file:")
        print("   1. Copy ENV_TEMPLATE.txt to .env")
        print("   2. Edit .env and add your DATABASE_URL")
        print("\n   Or run: copy ENV_TEMPLATE.txt .env")
        return False

def check_database_url():
    """Check if DATABASE_URL is set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    if db_url and 'postgresql' in db_url.lower():
        print(f"✅ DATABASE_URL is set")
        print(f"   Connection: {db_url[:60]}...")
        return True
    else:
        print("❌ DATABASE_URL not set or not PostgreSQL")
        print("\n📝 Add to .env file:")
        print("   DATABASE_URL=postgresql://user:password@host:port/database")
        return False

def check_json_files():
    """Check which JSON files exist"""
    json_files = [
        'users_data.json',
        'trade_history.json',
        'signals_db.json',
        'user_notifications.json',
        'user_profiles.json',
        'community_data.json',
        'referral_data.json',
        'paper_trading.json'
    ]
    
    existing = []
    for file in json_files:
        if Path(file).exists():
            existing.append(file)
    
    if existing:
        print(f"✅ Found {len(existing)} JSON files to migrate:")
        for file in existing:
            size = Path(file).stat().st_size
            print(f"   - {file} ({size:,} bytes)")
        return True
    else:
        print("⚠️  No JSON files found")
        print("   This is okay if you're starting fresh")
        return False

def run_test_connection():
    """Test database connection"""
    print("\n🔗 Testing database connection...")
    try:
        result = subprocess.run([sys.executable, "test_db_connection.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_dry_run():
    """Run dry-run migration"""
    print("\n🧪 Running dry-run migration (no changes will be made)...")
    try:
        result = subprocess.run([sys.executable, "migrate_to_postgresql.py", "--dry-run"],
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_actual_migration():
    """Run actual migration"""
    print("\n🚀 Running actual migration...")
    response = input("   This will migrate all data. Continue? (y/n): ")
    if response.lower() != 'y':
        print("   Migration cancelled")
        return False
    
    try:
        result = subprocess.run([sys.executable, "migrate_to_postgresql.py", "--backup"],
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_migration():
    """Verify migration was successful"""
    print("\n🔍 Verifying migration...")
    try:
        result = subprocess.run([sys.executable, "verify_migration.py"],
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header("Database Migration Quick Start")
    
    print("This script will guide you through migrating from JSON to PostgreSQL.")
    print("\nPrerequisites:")
    print("  1. PostgreSQL database set up (Railway, DigitalOcean, or local)")
    print("  2. DATABASE_URL in .env file")
    print("  3. Dependencies installed (psycopg2-binary, sqlalchemy)")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Check .env file
    print_header("Step 1: Check Environment Setup")
    if not check_env_file():
        print("\n⚠️  Please create .env file first")
        return
    
    # Step 2: Check DATABASE_URL
    if not check_database_url():
        print("\n⚠️  Please set DATABASE_URL in .env file")
        return
    
    # Step 3: Check JSON files
    print_header("Step 2: Check JSON Files")
    check_json_files()
    
    # Step 4: Test connection
    print_header("Step 3: Test Database Connection")
    if not run_test_connection():
        print("\n⚠️  Database connection failed. Please fix DATABASE_URL")
        return
    
    # Step 5: Dry run
    print_header("Step 4: Dry-Run Migration")
    response = input("Run dry-run migration? (y/n): ")
    if response.lower() == 'y':
        if not run_dry_run():
            print("\n⚠️  Dry-run failed. Please check errors above")
            return
        print("\n✅ Dry-run successful!")
        response = input("\nProceed with actual migration? (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled")
            return
    else:
        print("Skipping dry-run...")
    
    # Step 6: Actual migration
    print_header("Step 5: Run Actual Migration")
    if not run_actual_migration():
        print("\n⚠️  Migration failed. Check errors above")
        return
    
    # Step 7: Verify
    print_header("Step 6: Verify Migration")
    verify_migration()
    
    # Success!
    print_header("✅ Migration Complete!")
    print("Next steps:")
    print("  1. Test bot: python telegram_bot.py")
    print("  2. Verify bot uses PostgreSQL")
    print("  3. Set up automated backups (Week 1, Day 5)")
    print("\n🎉 Congratulations! Your database is migrated!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

