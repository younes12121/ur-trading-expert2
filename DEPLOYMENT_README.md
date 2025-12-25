# 🚀 UR Trading Expert Production Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or Debian 11+
- Python 3.11+
- Domain name pointing to your server
- Root or sudo access

## Quick Deploy (Automated)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ur-trading-expert
```

### 2. Configure Deployment
```bash
# Edit deployment config
nano deploy_config.json

# Update these values:
# - domain: "yourdomain.com"
# - email: "admin@yourdomain.com"
```

### 3. Run Automated Deployment
```bash
# Make deployment script executable
chmod +x deploy_production.py

# Run deployment (will prompt for sudo)
python3 deploy_production.py --domain yourdomain.com --email admin@yourdomain.com
```

## Manual Deployment

### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx ufw git
```

### 2. Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_production.txt
```

### 3. Configure Environment
```bash
# Copy environment template
cp env.production.template .env

# Edit with your actual values
nano .env
```

### 4. Nginx Configuration
```bash
# Copy nginx config
sudo cp nginx.prod.conf /etc/nginx/sites-available/ur-trading-expert

# Enable site
sudo ln -s /etc/nginx/sites-available/ur-trading-expert /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Setup
```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com --email admin@yourdomain.com --agree-tos

# Set up auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -
```

### 6. Systemd Services
```bash
# Create service
sudo nano /etc/systemd/system/ur-dashboard.service

# Add service content (see deploy_production.py for template)

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ur-dashboard.service
sudo systemctl start ur-dashboard.service
```

### 7. Firewall
```bash
sudo ufw enable
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

## Docker Deployment (Alternative)

### Using Docker Compose
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f dashboard-api
```

### Using Docker Only
```bash
# Build image
docker build -t ur-trading-expert .

# Run container
docker run -d \
  --name ur-trading-dashboard \
  -p 5001:5001 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  ur-trading-expert
```

## Post-Deployment Checklist

- [ ] HTTPS working: `https://yourdomain.com`
- [ ] API health check: `https://yourdomain.com/api/health`
- [ ] Mobile app accessible: `https://yourdomain.com/mobile/`
- [ ] Dashboard working: `https://yourdomain.com/dashboard/`
- [ ] SSL certificate valid
- [ ] Services auto-starting on boot
- [ ] Logs rotating properly
- [ ] Firewall configured
- [ ] Backups configured

## Monitoring & Maintenance

### View Logs
```bash
# Application logs
sudo journalctl -u ur-dashboard.service -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Update Deployment
```bash
# Pull latest changes
git pull origin main

# Run deployment script
./deploy.sh

# Or manually
source venv/bin/activate
pip install -r requirements_production.txt
sudo systemctl restart ur-dashboard.service
sudo systemctl reload nginx
```

### Backup
```bash
# Database backup (if using PostgreSQL)
docker exec ur-trading-postgres pg_dump -U trading_user trading_expert > backup.sql

# Application data
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/ backups/
```

## Troubleshooting

### Common Issues

1. **Port 80/443 already in use**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop apache2  # if Apache is running
   ```

2. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew --force-renewal
   ```

3. **Service not starting**
   ```bash
   sudo systemctl status ur-dashboard.service
   sudo journalctl -u ur-dashboard.service --no-pager | tail -50
   ```

4. **Permission issues**
   ```bash
   sudo chown -R $USER:$USER /path/to/project
   sudo chmod -R 755 /path/to/project
   ```

## Performance Optimization

### Gunicorn Configuration
- Adjust worker count based on CPU cores
- Use gevent for async operations
- Configure timeouts appropriately

### Nginx Optimization
- Enable gzip compression
- Set up proper caching headers
- Configure rate limiting

### Database Optimization
- Use connection pooling
- Set up proper indexing
- Configure backup schedules

## Security Best Practices

- Keep dependencies updated
- Use strong passwords
- Enable fail2ban
- Monitor logs regularly
- Set up automated backups
- Use environment variables for secrets

## Support

For issues or questions:
1. Check the logs first
2. Verify configuration files
3. Test API endpoints manually
4. Check system resources

---

**🎉 Your UR Trading Expert is now live in production!**
