# Railway.app Setup Guide

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub account (for repository connection, optional)

## Step 1: Install Railway CLI

### Windows (PowerShell)
```powershell
# Option 1: Using npm (if you have Node.js installed)
npm i -g @railway/cli

# Option 2: Using Scoop (if you have Scoop)
scoop bucket add railway https://github.com/railwayapp/scoop-bucket.git
scoop install railway

# Option 3: Download binary directly
# Visit: https://github.com/railwayapp/cli/releases
# Download railway-windows-amd64.exe
# Rename to railway.exe and add to PATH
```

### Mac/Linux
```bash
# Using npm
npm i -g @railway/cli

# Or using Homebrew (Mac)
brew install railway

# Or download binary from GitHub releases
```

### Verify Installation
```bash
railway --version
```

## Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate. After login, you'll be redirected back to the terminal.

## Step 3: Create New Project

```bash
# Navigate to your project directory
cd C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting

# Initialize Railway project
railway init
```

This will:
- Create a new Railway project (or link to existing)
- Create `.railway` directory with project configuration

## Step 4: Add PostgreSQL Service

```bash
# Add PostgreSQL database
railway add postgresql
```

This will:
- Create a PostgreSQL database instance
- Automatically set `DATABASE_URL` environment variable
- Provide connection details

## Step 5: Set Environment Variables

```bash
# View current variables
railway variables

# Set Telegram bot token
railway variables set TELEGRAM_BOT_TOKEN=your_token_here

# Set Stripe keys (test mode for now)
railway variables set STRIPE_SECRET_KEY=sk_test_your_key
railway variables set STRIPE_PREMIUM_PRICE_ID=price_test_premium
railway variables set STRIPE_VIP_PRICE_ID=price_test_vip

# Set other optional variables
railway variables set LOG_LEVEL=INFO
railway variables set HEALTH_CHECK_ENABLED=true
railway variables set BACKUP_ENABLED=true
```

Or use Railway dashboard:
1. Go to https://railway.app
2. Select your project
3. Go to "Variables" tab
4. Add variables manually

## Step 6: Deploy

### Option A: Deploy from Local (Quick Test)
```bash
railway up
```

### Option B: Deploy from GitHub (Recommended)
1. Push your code to GitHub repository
2. In Railway dashboard:
   - Go to your project
   - Click "New" → "GitHub Repo"
   - Select your repository
   - Railway will auto-deploy on every push

## Step 7: Run Database Migration

After deployment, run migration on Railway:

```bash
railway run python migrate_to_postgresql.py
```

Or use Railway dashboard:
1. Go to your project
2. Click on your service
3. Go to "Deployments" tab
4. Click "Run Command"
5. Enter: `python migrate_to_postgresql.py`

## Step 8: Verify Deployment

1. Check logs:
```bash
railway logs
```

2. Check health endpoint:
```bash
# Get your Railway URL
railway domain

# Visit: https://your-app.railway.app/health
```

## Step 9: Set Up Monitoring

1. Get your Railway app URL
2. Set up UptimeRobot:
   - Go to https://uptimerobot.com
   - Add new monitor
   - Type: HTTP(s)
   - URL: `https://your-app.railway.app/health`
   - Interval: 5 minutes

## Troubleshooting

### Railway CLI not found
- Make sure Railway CLI is in your PATH
- Try: `npm i -g @railway/cli` again

### Database connection fails
- Verify `DATABASE_URL` is set: `railway variables`
- Check database is running in Railway dashboard

### Deployment fails
- Check logs: `railway logs`
- Verify `Procfile` exists and is correct
- Check `requirements.txt` has all dependencies

### Migration fails
- Ensure database is accessible
- Check migration script has no errors
- Verify JSON files exist locally

## Next Steps

After Railway setup:
1. ✅ Database migration complete
2. ✅ Bot deployed and running
3. ✅ Health check accessible
4. ⏭️ Set up UptimeRobot monitoring
5. ⏭️ Configure automated backups
6. ⏭️ Test all bot commands

## Useful Commands

```bash
# View project status
railway status

# View logs
railway logs --follow

# Run command in Railway environment
railway run python script.py

# Open Railway dashboard
railway open

# View environment variables
railway variables

# Connect to database shell
railway connect postgres
```
