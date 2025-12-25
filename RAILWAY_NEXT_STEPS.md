# Railway Setup - Next Steps

## ✅ Railway CLI Installed Successfully!

Railway CLI v4.12.0 has been downloaded and extracted to `railway-cli\railway.exe`

## Step 1: Login to Railway (REQUIRES BROWSER)

**You need to run this command manually** (it will open your browser):

**In PowerShell:**
```powershell
.\railway-cli\railway.exe login
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe login
```

Or use the helper script:
```bash
railway_setup.bat login
```

This will:
1. Open your browser
2. Ask you to sign in to Railway (or create account)
3. Authorize the CLI
4. Return to terminal when done

## Step 2: Initialize Railway Project

After login, run:

**In PowerShell:**
```powershell
.\railway-cli\railway.exe init
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe init
```

This will:
- Create a new Railway project (or link to existing)
- Create `.railway` directory with project config

## Step 3: Add PostgreSQL Database

**In PowerShell:**
```powershell
.\railway-cli\railway.exe add postgresql
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe add postgresql
```

This will:
- Create a PostgreSQL database instance
- Automatically set `DATABASE_URL` environment variable
- Provide connection details

## Step 4: Get Database URL

**In PowerShell:**
```powershell
.\railway-cli\railway.exe variables
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe variables
```

Look for `DATABASE_URL` - copy this value. You'll need it for migration.

## Step 5: Set Environment Variables

Set your Telegram bot token and Stripe keys:

**In PowerShell:**
```powershell
.\railway-cli\railway.exe variables set TELEGRAM_BOT_TOKEN=your_token_here
.\railway-cli\railway.exe variables set STRIPE_SECRET_KEY=sk_test_your_key
.\railway-cli\railway.exe variables set STRIPE_PREMIUM_PRICE_ID=price_test_premium
.\railway-cli\railway.exe variables set STRIPE_VIP_PRICE_ID=price_test_vip
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe variables set TELEGRAM_BOT_TOKEN=your_token_here
railway-cli\railway.exe variables set STRIPE_SECRET_KEY=sk_test_your_key
railway-cli\railway.exe variables set STRIPE_PREMIUM_PRICE_ID=price_test_premium
railway-cli\railway.exe variables set STRIPE_VIP_PRICE_ID=price_test_vip
```

Or use Railway dashboard:
1. Go to https://railway.app
2. Select your project
3. Go to "Variables" tab
4. Add variables manually

## Step 6: Run Database Migration

Once you have DATABASE_URL, run migration:

```bash
python migrate_to_postgresql.py --database-url "your_database_url_here"
```

Or on Railway (after deployment):
**In PowerShell:**
```powershell
.\railway-cli\railway.exe run python migrate_to_postgresql.py
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe run python migrate_to_postgresql.py
```

## Step 7: Deploy to Railway

**In PowerShell:**
```powershell
.\railway-cli\railway.exe up
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe up
```

This will:
- Build your application
- Deploy to Railway
- Start the bot

## Step 8: View Logs

**In PowerShell:**
```powershell
.\railway-cli\railway.exe logs --follow
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe logs --follow
```

## Step 9: Get Your App URL

**In PowerShell:**
```powershell
.\railway-cli\railway.exe domain
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe domain
```

Or check Railway dashboard for your app URL.

## Quick Reference

All Railway commands use the format:

**In PowerShell:**
```powershell
.\railway-cli\railway.exe <command>
```

**In Command Prompt:**
```cmd
railway-cli\railway.exe <command>
```

Or use the helper script:
```bash
railway_setup.bat <command>
```

## Troubleshooting

### "Cannot login in non-interactive mode"
- This is normal - you must run `railway login` manually in your terminal
- It requires browser interaction

### "Command not found" or "Could not be loaded"
- **In PowerShell**: Use `.\railway-cli\railway.exe` (with `.\` prefix)
- **In Command Prompt**: Use `railway-cli\railway.exe` (without `.\`)
- Or add `railway-cli` to your system PATH

### Database connection fails
- Verify DATABASE_URL is set: `railway-cli\railway.exe variables`
- Check database is running in Railway dashboard

## What's Next?

After completing these steps:
1. ✅ Bot will be running 24/7 on Railway
2. ✅ Database will be PostgreSQL (production-ready)
3. ✅ All data migrated from JSON
4. ⏭️ Set up UptimeRobot monitoring (use health endpoint URL)
5. ⏭️ Configure automated backups

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Dashboard: https://railway.app
- See `RAILWAY_SETUP_GUIDE.md` for detailed instructions
