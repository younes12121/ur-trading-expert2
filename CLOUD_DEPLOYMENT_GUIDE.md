# ☁️ Cloud Deployment Guide - AWS & DigitalOcean

**Estimated Time:** 1-2 hours  
**Cost:** $5-20/month depending on platform  
**Difficulty:** Intermediate

---

## 🎯 PLATFORM COMPARISON

| Feature | DigitalOcean | AWS EC2 | Railway.app |
|---------|--------------|---------|-------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | $6/month | $8-15/month | $5/month (starter) |
| **Setup Time** | 30 min | 60 min | 15 min |
| **Scaling** | Good | Excellent | Good |
| **Free Tier** | $200 credit | 12 months free | $5/month free |
| **Recommended** | ✅ Best for beginners | ✅ Best for scale | ✅ Easiest setup |

**My Recommendation: Start with Railway.app** (easiest) or **DigitalOcean** (best value)

---

# OPTION 1: RAILWAY.APP (EASIEST - 15 MINUTES) 🚀

## Why Railway?
- ✅ **Easiest** deployment (literally 5 commands)
- ✅ **$5/month free** credit (enough for your bot)
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in database** (PostgreSQL)
- ✅ **Custom domains** included
- ✅ **Perfect for beginners**

---

## STEP 1: PREPARE YOUR BOT (5 minutes)

### 1.1 Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Mac/Linux
curl -fsSL https://railway.app/install.sh | sh
```

### 1.2 Login to Railway

```bash
railway login
```

This opens browser - create account or login.

### 1.3 Create Required Files

**Create `requirements.txt`:** (already exists, verify it)
```txt
python-telegram-bot==20.6
pandas==2.1.3
numpy==1.26.2
requests==2.31.0
python-dotenv==1.0.0
stripe==7.4.0
psycopg2-binary==2.9.9
yfinance==0.2.32
feedparser==6.0.10
beautifulsoup4==4.12.2
```

**Create `runtime.txt`:**
```txt
python-3.11.6
```

**Create `Procfile`:**
```txt
worker: python telegram_bot.py
```

**Create `.gitignore`:**
```txt
.env
__pycache__/
*.pyc
*.log
*.db
bot_config.py
.venv/
venv/
```

---

## STEP 2: DEPLOY TO RAILWAY (5 minutes)

### 2.1 Initialize Project

```bash
cd C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting
railway init
```

Choose: **"Create new project"**
Name: **"trading-bot"**

### 2.2 Add PostgreSQL Database

```bash
railway add
```

Select: **PostgreSQL**

Railway automatically creates database and provides connection string.

### 2.3 Set Environment Variables

```bash
railway variables set TELEGRAM_BOT_TOKEN=your_token_here
railway variables set STRIPE_SECRET_KEY=your_stripe_key
railway variables set STRIPE_PREMIUM_PRICE_ID=your_price_id
railway variables set STRIPE_VIP_PRICE_ID=your_vip_price_id
```

Or set them in Railway dashboard: https://railway.app/dashboard

### 2.4 Deploy!

```bash
railway up
```

This uploads your code and starts the bot. Done! ✅

### 2.5 Check Logs

```bash
railway logs
```

You should see: "Bot is running with AUTO-ALERTS!"

---

## STEP 3: GET YOUR BOT URL (For Webhooks)

```bash
railway domain
```

This gives you a URL like: `trading-bot-production-xxxx.up.railway.app`

Use this for:
- Stripe webhooks
- Landing page links
- API endpoints

---

# OPTION 2: DIGITALOCEAN (BEST VALUE - 30 MINUTES) 💧

## Why DigitalOcean?
- ✅ **$6/month** for basic droplet (enough for 1000+ users)
- ✅ **$200 free credit** for new users (33 months free!)
- ✅ **Simple interface**
- ✅ **Great documentation**
- ✅ **Reliable uptime**

---

## STEP 1: CREATE DIGITALOCEAN ACCOUNT

1. Go to: https://www.digitalocean.com
2. Sign up (use this link for $200 credit: https://try.digitalocean.com/freetrialoffer/)
3. Add payment method (won't charge for 60 days)
4. Verify email

---

## STEP 2: CREATE DROPLET (5 minutes)

### 2.1 Create New Droplet

1. Click **"Create"** → **"Droplets"**
2. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/month - 1GB RAM, 25GB SSD)
   - **Region:** Closest to you (e.g., New York, London)
   - **Authentication:** SSH Key (recommended) or Password
   - **Hostname:** trading-bot

3. Click **"Create Droplet"**

### 2.2 Get Your Droplet IP

After creation, copy the IP address (e.g., `167.99.123.456`)

---

## STEP 3: CONNECT TO YOUR DROPLET (2 minutes)

### Windows Users:

```powershell
# Use PowerShell or install PuTTY
ssh root@your_droplet_ip
```

### Mac/Linux Users:

```bash
ssh root@your_droplet_ip
```

Enter password when prompted.

---

## STEP 4: INSTALL DEPENDENCIES (10 minutes)

### 4.1 Update System

```bash
apt update && apt upgrade -y
```

### 4.2 Install Python 3.11

```bash
apt install python3.11 python3.11-venv python3-pip -y
```

### 4.3 Install PostgreSQL

```bash
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql
```

### 4.4 Install Git

```bash
apt install git -y
```

---

## STEP 5: SETUP YOUR BOT (10 minutes)

### 5.1 Create Bot User

```bash
adduser botuser
usermod -aG sudo botuser
su - botuser
```

### 5.2 Clone/Upload Your Bot

**Option A: Upload files directly**
```bash
mkdir ~/trading-bot
cd ~/trading-bot
# Upload your files using SCP or SFTP
```

**Option B: Use Git (if you have GitHub repo)**
```bash
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot
```

**Option C: Manual upload from Windows**
```powershell
# From your local machine
scp -r C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\* botuser@your_droplet_ip:~/trading-bot/
```

### 5.3 Create Virtual Environment

```bash
cd ~/trading-bot
python3.11 -m venv venv
source venv/bin/activate
```

### 5.4 Install Requirements

```bash
pip install -r requirements.txt
```

### 5.5 Create .env File

```bash
nano .env
```

Paste:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_PREMIUM_PRICE_ID=your_premium_price_id
STRIPE_VIP_PRICE_ID=your_vip_price_id
DATABASE_URL=postgresql://botuser:password@localhost/trading_bot
```

Save: `Ctrl + X`, then `Y`, then `Enter`

---

## STEP 6: SETUP DATABASE (5 minutes)

### 6.1 Create Database

```bash
sudo -u postgres psql
```

In PostgreSQL:
```sql
CREATE DATABASE trading_bot;
CREATE USER botuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO botuser;
\q
```

### 6.2 Initialize Database

```bash
python database.py
```

---

## STEP 7: RUN BOT AS SERVICE (10 minutes)

### 7.1 Create Systemd Service

```bash
sudo nano /etc/systemd/system/trading-bot.service
```

Paste:
```ini
[Unit]
Description=Trading Bot
After=network.target postgresql.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/trading-bot
Environment="PATH=/home/botuser/trading-bot/venv/bin"
ExecStart=/home/botuser/trading-bot/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl + X`, `Y`, `Enter`

### 7.2 Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl start trading-bot
sudo systemctl enable trading-bot
```

### 7.3 Check Status

```bash
sudo systemctl status trading-bot
```

Should show: **Active: active (running)**

### 7.4 View Logs

```bash
sudo journalctl -u trading-bot -f
```

---

## STEP 8: SETUP FIREWALL (2 minutes)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

# OPTION 3: AWS EC2 (MOST SCALABLE - 60 MINUTES) ☁️

## Why AWS?
- ✅ **12 months free** tier
- ✅ **Best for scaling** to thousands of users
- ✅ **Professional infrastructure**
- ✅ **Advanced features** (load balancing, auto-scaling)

---

## QUICK AWS SETUP

### 1. Create AWS Account
- Go to: https://aws.amazon.com
- Sign up (requires credit card but free tier available)

### 2. Launch EC2 Instance
1. Go to EC2 Dashboard
2. Click **"Launch Instance"**
3. Choose:
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance Type:** t2.micro (free tier eligible)
   - **Storage:** 8GB (free tier)
4. Create key pair (download `.pem` file)
5. Launch instance

### 3. Connect to Instance

```bash
# Windows (use Git Bash or WSL)
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# Mac/Linux
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### 4. Follow DigitalOcean Steps 4-8

The setup is identical to DigitalOcean after connecting!

---

## 🔒 SECURITY BEST PRACTICES

### Essential Security Steps

1. **Change Default Passwords**
```bash
passwd  # Change root password
```

2. **Setup Firewall**
```bash
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp  # HTTPS
```

3. **Create Non-Root User**
```bash
adduser botuser
usermod -aG sudo botuser
```

4. **Disable Root Login**
```bash
sudo nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
sudo systemctl restart ssh
```

5. **Setup SSH Keys** (More secure than passwords)
```bash
ssh-keygen -t rsa -b 4096
# Copy public key to server
ssh-copy-id botuser@your_server_ip
```

6. **Install Fail2Ban** (Blocks brute force attacks)
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

---

## 📊 MONITORING YOUR BOT

### Check Bot Status

```bash
# Railway
railway logs

# DigitalOcean/AWS
sudo systemctl status trading-bot
sudo journalctl -u trading-bot -f
```

### Check Resource Usage

```bash
htop  # CPU and memory
df -h  # Disk space
free -h  # RAM usage
```

### Setup Monitoring (Optional)

Install monitoring tools:
```bash
# Install Netdata (beautiful real-time monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

Access at: `http://your-server-ip:19999`

---

## 🔄 UPDATING YOUR BOT

### Railway (Easiest)

```bash
# Just push to Git or run:
railway up
```

### DigitalOcean/AWS

```bash
ssh botuser@your_server_ip
cd ~/trading-bot
git pull  # If using Git
# Or upload new files
sudo systemctl restart trading-bot
```

---

## 💰 COST COMPARISON

### Monthly Costs

**Railway:**
- Free: $5 credit/month (enough for small bot)
- Hobby: $5/month (100GB transfer)
- Pro: $20/month (unlimited)

**DigitalOcean:**
- Basic: $6/month (1GB RAM, 25GB SSD, 1TB transfer)
- Better: $12/month (2GB RAM, 50GB SSD, 2TB transfer)
- Pro: $24/month (4GB RAM, 80GB SSD, 4TB transfer)

**AWS EC2:**
- Free: First 12 months (t2.micro)
- After: $8-10/month (t2.micro)
- Scaling: $20-50/month (t2.small/medium)

**Recommendation:**
- Start: **Railway** ($5/month or free)
- Growing: **DigitalOcean** ($6-12/month)
- Scale: **AWS** ($20-50/month)

---

## 🚨 TROUBLESHOOTING

### Bot Won't Start

```bash
# Check logs
sudo journalctl -u trading-bot -n 50

# Check Python errors
cd ~/trading-bot
source venv/bin/activate
python telegram_bot.py
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l
```

### Out of Memory

```bash
# Check memory usage
free -h

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Can't Connect via SSH

```bash
# Check firewall
sudo ufw status

# Allow SSH
sudo ufw allow 22/tcp
```

---

## ✅ DEPLOYMENT CHECKLIST

Before considering deployment complete:

- [ ] Server created and accessible
- [ ] Python and dependencies installed
- [ ] Bot files uploaded
- [ ] Database setup and initialized
- [ ] Environment variables configured
- [ ] Bot running as systemd service
- [ ] Bot starts automatically on reboot
- [ ] Firewall configured
- [ ] SSL certificate installed (if using webhooks)
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Tested all commands work
- [ ] Stripe webhooks updated with production URL
- [ ] Bot responds in Telegram ✅

---

## 🎉 CONGRATULATIONS!

Your bot is now live on the cloud! 🚀

### What You've Achieved:
✅ Bot running 24/7 on cloud server  
✅ Automatic restarts if crashes  
✅ Professional hosting setup  
✅ Ready for thousands of users  
✅ Monitoring in place  

### Next Steps:
1. ✅ Complete Stripe setup (if not done)
2. ✅ Create legal documents (ToS, Privacy)
3. ✅ Build landing page
4. ✅ Start marketing

---

**Your bot is LIVE and ready to make money! 💰**

