# ⚡ Quick Start: Database Migration

**Time:** 30-60 minutes  
**Difficulty:** Easy (with this guide)

---

## 🚀 Fastest Path (3 Steps)

### Step 1: Set Up PostgreSQL (15 min)

**Option A: Railway.app (Easiest)**
1. Go to https://railway.app
2. Sign up → New Project → Add PostgreSQL
3. Copy `DATABASE_URL` from Variables tab

**Option B: Local (For Testing)**
1. Download from https://www.postgresql.org/download/
2. Install with default settings
3. Create database: `CREATE DATABASE trading_bot;`
4. Connection: `postgresql://postgres:YOUR_PASSWORD@localhost:5432/trading_bot`

---

### Step 2: Configure Environment (5 min)

```powershell
# Create .env file
copy ENV_TEMPLATE.txt .env

# Edit .env and add:
DATABASE_URL=postgresql://user:password@host:port/database
```

---

### Step 3: Run Migration (10 min)

**Option A: Interactive Script (Easiest)**
```powershell
python run_migration.py
```
Follow the prompts!

**Option B: Manual Steps**
```powershell
# 1. Test connection
python test_db_connection.py

# 2. Dry-run (test first)
python migrate_to_postgresql.py --dry-run

# 3. Actual migration
python migrate_to_postgresql.py --backup

# 4. Verify
python verify_migration.py
```

---

## ✅ Success Checklist

- [ ] PostgreSQL database set up
- [ ] DATABASE_URL in .env file
- [ ] Connection test passes
- [ ] Dry-run shows data to migrate
- [ ] Migration completes with 0 errors
- [ ] Verification shows data in database

---

## 🆘 Quick Troubleshooting

**"DATABASE_URL not set"**
→ Create `.env` file and add `DATABASE_URL=...`

**"Connection refused"**
→ Check PostgreSQL is running (local) or connection string is correct (cloud)

**"No data migrated"**
→ Check JSON files exist and have data

**"Table already exists"**
→ Normal! Migration will still work

---

## 📚 Full Guide

For detailed instructions, see:
- **`WEEK1_DAY1_DATABASE_MIGRATION.md`** ← Complete step-by-step guide

---

## 🎯 What's Next?

After migration:
1. Test bot: `python telegram_bot.py`
2. Verify bot uses PostgreSQL
3. Continue to Day 2: Production Hosting

---

**Ready?** Run: `python run_migration.py`

