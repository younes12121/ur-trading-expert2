# 📦 Week 1, Day 1: Database Migration Guide

**Goal:** Migrate from JSON files to PostgreSQL database  
**Time:** 2-4 hours  
**Difficulty:** Intermediate

---

## 🎯 Overview

You're currently using JSON files for data storage. To scale beyond 100 users and prepare for production, we need to migrate to PostgreSQL.

**Current State:**
- ✅ JSON files storing user data, trades, signals
- ✅ Migration script ready (`migrate_to_postgresql.py`)
- ✅ Database models ready (`database.py`)

**Target State:**
- ✅ PostgreSQL database running
- ✅ All JSON data migrated
- ✅ Bot using PostgreSQL instead of JSON

---

## 📋 Step 1: Choose Your PostgreSQL Setup (30 minutes)

You have 3 options. Choose based on your needs:

### Option A: Railway.app PostgreSQL (EASIEST - Recommended) ⭐

**Best for:** Quick setup, free tier available, cloud-hosted

**Steps:**
1. **Sign up at Railway.app**
   - Go to: https://railway.app
   - Click "Start a New Project"
   - Sign up with GitHub (easiest)

2. **Create PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically creates database
   - Copy the `DATABASE_URL` (looks like: `postgresql://postgres:password@host:port/railway`)

3. **Get Connection String**
   - Click on your PostgreSQL service
   - Go to "Variables" tab
   - Copy `DATABASE_URL` value

**Cost:** Free tier available ($5/month after)

**Time:** 15 minutes

---

### Option B: Local PostgreSQL (For Testing)

**Best for:** Testing migration locally before deploying

**Steps (Windows):**
1. **Download PostgreSQL**
   - Go to: https://www.postgresql.org/download/windows/
   - Download installer
   - Install with default settings
   - Remember the password you set!

2. **Create Database**
   ```powershell
   # Open pgAdmin (installed with PostgreSQL)
   # Or use command line:
   psql -U postgres
   CREATE DATABASE trading_bot;
   \q
   ```

3. **Get Connection String**
   ```
   postgresql://postgres:YOUR_PASSWORD@localhost:5432/trading_bot
   ```

**Cost:** Free

**Time:** 30 minutes

---

### Option C: DigitalOcean PostgreSQL (Production-Ready)

**Best for:** Production deployment, more control

**Steps:**
1. **Sign up at DigitalOcean**
   - Go to: https://www.digitalocean.com
   - Create account ($200 free credit)

2. **Create Managed Database**
   - Click "Create" → "Databases"
   - Choose PostgreSQL 15
   - Choose $15/month plan (or $6/month for basic)
   - Choose region closest to you
   - Create database

3. **Get Connection String**
   - Click on your database
   - Go to "Connection Details"
   - Copy connection string

**Cost:** $6-15/month

**Time:** 20 minutes

---

## 📋 Step 2: Set Up Environment Variables (5 minutes)

1. **Create or Update `.env` file**

   In your `backtesting` directory, create/update `.env`:

   ```bash
   # Copy from ENV_TEMPLATE.txt if needed
   cp ENV_TEMPLATE.txt .env
   ```

2. **Add DATABASE_URL**

   Edit `.env` and set your PostgreSQL connection:

   ```bash
   # For Railway.app
   DATABASE_URL=postgresql://postgres:password@host.railway.app:5432/railway

   # For Local PostgreSQL
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/trading_bot

   # For DigitalOcean
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

   **Important:** Replace with your actual connection string!

3. **Verify `.env` file exists**

   ```powershell
   cd C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting
   Test-Path .env
   ```

   Should return `True`

---

## 📋 Step 3: Test Database Connection (10 minutes)

1. **Install dependencies** (if not already installed)

   ```powershell
   pip install psycopg2-binary sqlalchemy python-dotenv
   ```

2. **Test connection**

   Create a test script:

   ```python
   # test_db_connection.py
   import os
   from dotenv import load_dotenv
   from database import DatabaseManager

   load_dotenv()
   
   db_url = os.getenv('DATABASE_URL')
   if not db_url:
       print("❌ DATABASE_URL not set in .env file")
       exit(1)
   
   print(f"🔗 Connecting to: {db_url[:50]}...")
   
   try:
       db = DatabaseManager(db_url)
       db.create_tables()
       print("✅ Database connection successful!")
       print("✅ Tables created successfully!")
   except Exception as e:
       print(f"❌ Connection failed: {e}")
       exit(1)
   ```

3. **Run test**

   ```powershell
   python test_db_connection.py
   ```

   **Expected output:**
   ```
   🔗 Connecting to: postgresql://postgres:password@host...
   ✅ Database connection successful!
   ✅ Tables created successfully!
   ```

   **If you see errors:**
   - Check DATABASE_URL is correct
   - Verify PostgreSQL is running (for local)
   - Check firewall settings (for cloud)
   - Verify credentials

---

## 📋 Step 4: Backup JSON Files (5 minutes)

**IMPORTANT:** Always backup before migration!

The migration script will automatically backup, but let's verify:

1. **Check which JSON files exist**

   ```powershell
   Get-ChildItem *.json | Select-Object Name
   ```

   You should see files like:
   - `users_data.json`
   - `trade_history.json`
   - `signals_db.json`
   - `user_notifications.json`
   - `user_profiles.json`
   - `community_data.json`
   - `referral_data.json`
   - `paper_trading.json`

2. **Manual backup (optional but recommended)**

   ```powershell
   # Create backup folder
   $backupDir = "backup_json_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
   New-Item -ItemType Directory -Path $backupDir
   
   # Copy all JSON files
   Copy-Item *.json -Destination $backupDir
   
   Write-Host "✅ Backed up to: $backupDir"
   ```

---

## 📋 Step 5: Run Dry-Run Migration (10 minutes)

**Always test first!** This shows what will happen without making changes.

```powershell
python migrate_to_postgresql.py --dry-run
```

**Expected output:**
```
============================================================
🚀 Starting Database Migration (JSON → PostgreSQL)
============================================================

⚠️  DRY RUN MODE - No changes will be made to database

🔧 Initializing database...

📦 Migrating users...
  [DRY RUN] Would migrate user 123456789
  [DRY RUN] Would migrate user 987654321
✅ [DRY RUN] Would migrate 2 users

📦 Migrating trades...
  [DRY RUN] Would migrate trade for user 1
✅ [DRY RUN] Would migrate 1 trades

📦 Migrating signals...
  [DRY RUN] Would migrate signal 1
✅ [DRY RUN] Would migrate 10 signals

============================================================
📊 Migration Summary
============================================================
Users migrated:        2
Trades migrated:       1
Signals migrated:      10
Notifications migrated: 2
Errors:                0

✅ Migration complete!
⚠️  This was a dry run. Run without --dry-run to perform actual migration.
```

**If you see errors:**
- Check JSON file format
- Verify database connection
- Check file permissions

---

## 📋 Step 6: Run Actual Migration (15 minutes)

Once dry-run looks good, run the real migration:

```powershell
python migrate_to_postgresql.py --backup
```

**What this does:**
1. ✅ Creates backup of all JSON files
2. ✅ Migrates users from `users_data.json`
3. ✅ Migrates trades from `trade_history.json`
4. ✅ Migrates signals from `signals_db.json`
5. ✅ Migrates notifications from `user_notifications.json`
6. ✅ Shows summary of what was migrated

**Expected output:**
```
============================================================
🚀 Starting Database Migration (JSON → PostgreSQL)
============================================================

📦 Creating backup of JSON files...
✅ Backed up users_data.json
✅ Backed up trade_history.json
✅ Backed up signals_db.json
✅ All JSON files backed up to backup_json_20250108_120000/

🔧 Initializing database...

📦 Migrating users...
✅ Migrated 2 users

📦 Migrating trades...
✅ Migrated 1 trades

📦 Migrating signals...
✅ Migrated 10 signals

📦 Migrating user notifications...
✅ Migrated 2 notification settings

============================================================
📊 Migration Summary
============================================================
Users migrated:        2
Trades migrated:       1
Signals migrated:      10
Notifications migrated: 2
Errors:                0

✅ Migration complete!
```

**If migration fails:**
- Check error messages
- Verify JSON files are valid (not corrupted)
- Check database connection
- Restore from backup if needed

---

## 📋 Step 7: Verify Migration (10 minutes)

1. **Check database has data**

   Create verification script:

   ```python
   # verify_migration.py
   import os
   from dotenv import load_dotenv
   from database import DatabaseManager, User, Trade, Signal

   load_dotenv()
   
   db = DatabaseManager(os.getenv('DATABASE_URL'))
   session = db.get_session()
   
   # Count records
   user_count = session.query(User).count()
   trade_count = session.query(Trade).count()
   signal_count = session.query(Signal).count()
   
   print(f"📊 Database Statistics:")
   print(f"   Users: {user_count}")
   print(f"   Trades: {trade_count}")
   print(f"   Signals: {signal_count}")
   
   # Show sample user
   if user_count > 0:
       user = session.query(User).first()
       print(f"\n👤 Sample User:")
       print(f"   Telegram ID: {user.telegram_id}")
       print(f"   Tier: {user.tier.value}")
       print(f"   Created: {user.created_at}")
   
   session.close()
   ```

   Run:
   ```powershell
   python verify_migration.py
   ```

2. **Compare with JSON files**

   Count records in JSON vs database - should match!

---

## 📋 Step 8: Update Bot to Use PostgreSQL (30 minutes)

Now we need to ensure the bot uses PostgreSQL instead of JSON.

1. **Check current data storage**

   The bot should automatically use PostgreSQL if `DATABASE_URL` is set. Let's verify:

   ```python
   # test_bot_db.py
   import os
   from dotenv import load_dotenv
   from database import DatabaseManager
   from user_manager import UserManager

   load_dotenv()
   
   # Check if DATABASE_URL is set
   db_url = os.getenv('DATABASE_URL')
   if db_url and 'postgresql' in db_url:
       print("✅ Bot will use PostgreSQL")
       print(f"   Connection: {db_url[:50]}...")
   else:
       print("⚠️  Bot will use JSON files (DATABASE_URL not set or not PostgreSQL)")
   ```

2. **Test bot commands**

   Start the bot and test:
   ```powershell
   python telegram_bot.py
   ```

   In Telegram, test:
   - `/start` - Should create user in PostgreSQL
   - `/profile` - Should read from PostgreSQL
   - `/analytics` - Should read trades from PostgreSQL

3. **Verify data is being written to PostgreSQL**

   After testing bot commands, run `verify_migration.py` again to see new records.

---

## 📋 Step 9: Keep JSON as Backup (Optional)

You can keep JSON files as backup, but the bot should now use PostgreSQL.

**Recommended:**
- Keep JSON files in backup folder
- Delete or archive original JSON files after 1 week of successful operation
- Set up automated PostgreSQL backups (see Week 1, Day 5)

---

## ✅ Success Checklist

Before moving to Day 2, verify:

- [ ] PostgreSQL database is set up and running
- [ ] `DATABASE_URL` is set in `.env` file
- [ ] Database connection test passes
- [ ] Dry-run migration completed successfully
- [ ] Actual migration completed with 0 errors
- [ ] Verification shows data in database
- [ ] Bot can read/write to PostgreSQL
- [ ] JSON files are backed up

---

## 🆘 Troubleshooting

### Error: "DATABASE_URL not set"
**Solution:** 
- Check `.env` file exists
- Verify `DATABASE_URL` is in `.env`
- Make sure you're loading `.env` (using `python-dotenv`)

### Error: "Connection refused" or "Could not connect"
**Solution:**
- Verify PostgreSQL is running (for local)
- Check connection string is correct
- Verify firewall allows connection (for cloud)
- Check credentials are correct

### Error: "Table already exists"
**Solution:**
- This is normal if tables were created before
- Migration will still work
- Or drop tables first: `python -c "from database import DatabaseManager; db = DatabaseManager(); db.drop_tables(); db.create_tables()"`

### Error: "Invalid JSON" or "JSON decode error"
**Solution:**
- Check JSON files are valid
- Try opening JSON file in text editor
- Fix any syntax errors
- Restore from backup if needed

### Migration shows 0 records
**Solution:**
- Check JSON files exist and have data
- Verify JSON file format matches expected structure
- Check file permissions
- Look at error messages for details

---

## 📚 Next Steps

Once migration is complete:

1. **Day 2:** Continue with database optimization
2. **Day 3-4:** Set up production hosting
3. **Day 5:** Set up monitoring and backups

**You're done with Day 1 when:**
- ✅ All data migrated to PostgreSQL
- ✅ Bot is using PostgreSQL
- ✅ No errors in migration

---

## 🎉 Congratulations!

You've successfully migrated from JSON to PostgreSQL! Your bot is now ready to scale to thousands of users.

**Time spent:** 2-4 hours  
**Status:** ✅ Database migration complete

**Next:** Week 1, Day 2 - Production Hosting Setup

---

*Need help? Check the migration script comments or review `database.py` for model definitions.*

