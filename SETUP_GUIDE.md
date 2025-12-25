# 🚀 Trading Bot Setup Guide

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 13+ (or use JSON files for development)
- Telegram Bot Token
- Stripe Account (for payments)
- API Keys (Twitter, Reddit - optional)

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd antigravity/scratch/smc_trading_analysis/backtesting
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the backtesting directory:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database (PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/trading_bot

# Stripe (Payment Processing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional: Social Media APIs
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=TradingBot/1.0

# Optional: News API
NEWS_API_KEY=...

# Admin User ID (your Telegram ID)
ADMIN_USER_ID=your_telegram_id
```

### 3. Set Up Database

#### Option A: PostgreSQL (Production)

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql postgresql-contrib
# Windows: Download from postgresql.org

# Create database
createdb trading_bot

# Initialize tables
python database.py
```

#### Option B: JSON Files (Development)

No setup needed - JSON files will be created automatically:
- `user_notifications.json`
- `user_profiles.json`
- `community_data.json`
- `referral_data.json`
- `broker_connections.json`
- `ml_model_data.json`
- `sentiment_data.json`

### 4. Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy your bot token
4. Add token to `.env` file

### 5. Configure Stripe (Optional - for payments)

1. Create account at stripe.com
2. Get API keys from Dashboard → Developers → API keys
3. Set up products:
   - Premium: $29/month
   - VIP: $99/month
4. Configure webhooks (see Stripe Setup below)
5. Add keys to `.env` file

---

## 🏃 Running the Bot

### Development Mode

```bash
python telegram_bot.py
```

### Production Mode (with systemd)

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=Trading Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/backtesting
ExecStart=/usr/bin/python3 telegram_bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

View logs:

```bash
sudo journalctl -u trading-bot -f
```

---

## 🔧 Configuration

### Update User Manager

Edit `user_manager.py` to configure feature access:

```python
self.feature_tiers = {
    "free": {
        "pairs": ["EURUSD", "GBPUSD"],
        "max_alerts_per_day": 1,
        # ...
    },
    "premium": {
        "pairs": "all",
        # ...
    }
}
```

### Update Payment Handler

Edit `payment_handler.py` with your Stripe product IDs:

```python
self.plans = {
    'premium': {
        'name': 'Premium',
        'price': 29,
        'stripe_price_id': 'price_...'  # Your Stripe price ID
    },
    # ...
}
```

---

## 💳 Stripe Setup (Detailed)

### 1. Create Products

In Stripe Dashboard → Products:

1. **Premium Plan**
   - Name: "Premium Trading Signals"
   - Price: $29/month recurring
   - Copy Price ID (e.g., `price_1ABC...`)

2. **VIP Plan**
   - Name: "VIP Trading Signals"
   - Price: $99/month recurring
   - Copy Price ID

3. **Trial Period** (optional)
   - Set 7-day trial on both products

### 2. Configure Webhooks

Dashboard → Developers → Webhooks → Add endpoint:

**Endpoint URL**: `https://yourdomain.com/stripe/webhook`

**Events to listen for**:
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

Copy webhook signing secret to `.env`

### 3. Test Mode vs Live Mode

- **Test Mode**: Use `sk_test_...` keys for development
- **Live Mode**: Switch to `sk_live_...` keys for production

---

## 🔗 API Integrations

### Twitter API

1. Apply for developer account: developer.twitter.com
2. Create app and get API keys
3. Add to `.env`
4. Uncomment Twitter code in `sentiment_analyzer.py`

### Reddit API

1. Go to reddit.com/prefs/apps
2. Create app (script type)
3. Get client ID and secret
4. Add to `.env`
5. Uncomment Reddit code in `sentiment_analyzer.py`

### Broker APIs

#### OANDA

1. Create account at oanda.com
2. Get API token from account settings
3. Users provide their own API key via `/broker connect oanda`

#### MetaTrader

1. Install MetaTrader5 Python package: `pip install MetaTrader5`
2. Uncomment MT5 code in `broker_connector.py`
3. Users provide login credentials via `/broker connect mt5`

---

## 🧪 Testing

### Manual Testing

1. Start bot: `python telegram_bot.py`
2. Open Telegram and search for your bot
3. Send `/start`
4. Test each command category:
   - Signals: `/eurusd`, `/gbpusd`
   - Education: `/learn`, `/glossary RSI`
   - Notifications: `/notifications`
   - Profile: `/profile`
   - Leaderboard: `/leaderboard winrate`

### Automated Testing (Optional)

```bash
pytest tests/
```

---

## 📊 Database Management

### Backup Database

```bash
pg_dump trading_bot > backup.sql
```

### Restore Database

```bash
psql trading_bot < backup.sql
```

### View Tables

```bash
psql trading_bot
\dt  # List tables
SELECT * FROM users LIMIT 10;
```

---

## 🐛 Troubleshooting

### Bot Not Responding

1. Check bot is running: `ps aux | grep telegram_bot`
2. Check logs for errors
3. Verify bot token in `.env`
4. Check internet connection

### Database Connection Error

1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check DATABASE_URL in `.env`
3. Test connection: `psql $DATABASE_URL`

### Stripe Webhook Not Working

1. Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8000/stripe/webhook`
2. Verify webhook secret in `.env`
3. Check webhook endpoint is publicly accessible

### Import Errors

1. Verify all dependencies installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (needs 3.9+)
3. Activate virtual environment if using one

---

## 🚀 Deployment (Production)

### Option 1: DigitalOcean Droplet

1. Create Droplet (Ubuntu 22.04, $12/mo minimum)
2. SSH into server
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip postgresql nginx
   ```
4. Clone repository
5. Set up systemd service (see above)
6. Configure firewall:
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

### Option 2: AWS EC2

1. Launch t3.small instance (Ubuntu)
2. Configure security group (SSH, HTTP, HTTPS)
3. Follow DigitalOcean steps above

### Option 3: Docker (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "telegram_bot.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgdata:
```

Run:

```bash
docker-compose up -d
```

---

## 📈 Monitoring

### Set Up Logging

Bot logs to console by default. For production:

```python
import logging

logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Rotation

Install logrotate:

```bash
sudo apt install logrotate
```

Create `/etc/logrotate.d/trading-bot`:

```
/path/to/trading_bot.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Error Tracking (Sentry)

1. Create account at sentry.io
2. Get DSN
3. Add to bot:

```python
import sentry_sdk

sentry_sdk.init(dsn="https://your-dsn@sentry.io/project")
```

---

## 🔒 Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use environment variables for secrets (never commit `.env`)
- [ ] Enable HTTPS for webhooks
- [ ] Encrypt broker credentials in database
- [ ] Set up firewall rules
- [ ] Enable PostgreSQL authentication
- [ ] Use strong passwords for database
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Add input validation
- [ ] Enable 2FA on Stripe/AWS accounts
- [ ] Review privacy policy and ToS with lawyer
- [ ] Implement GDPR compliance measures

---

## 📚 Additional Resources

- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [Stripe API Docs](https://stripe.com/docs/api)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Python-telegram-bot Docs](https://python-telegram-bot.readthedocs.io/)

---

## 🆘 Support

For issues or questions:

1. Check logs: `tail -f trading_bot.log`
2. Review error messages
3. Search documentation
4. Create GitHub issue (if applicable)

---

## ✅ Final Checklist

Before launch:

- [ ] All dependencies installed
- [ ] Database configured and initialized
- [ ] Environment variables set
- [ ] Telegram bot token working
- [ ] Stripe account set up (if monetizing)
- [ ] API keys configured (if using APIs)
- [ ] All commands tested
- [ ] Production hosting set up
- [ ] SSL certificate installed
- [ ] Monitoring configured
- [ ] Backups automated
- [ ] Security review complete
- [ ] Legal documents ready (ToS, Privacy)
- [ ] Marketing materials prepared

---

**🎉 You're ready to launch! Good luck! 🚀**
