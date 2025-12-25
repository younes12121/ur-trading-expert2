#!/usr/bin/env python3
"""
Production Deployment Script for UR Trading Expert
Deploys both Personal Dashboard API and Mobile App
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import argparse

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()

    def load_config(self):
        """Load deployment configuration"""
        config_path = self.project_root / 'deploy_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return {
                "domain": "your-domain.com",
                "email": "admin@your-domain.com",
                "ssl_auto": True,
                "dashboard_port": 5001,
                "mobile_port": 5002,
                "environment": "production",
                "nginx_config": True,
                "ssl_certbot": True,
                "monitoring": True
            }

    def run_command(self, command, cwd=None, check=True):
        """Run shell command with proper error handling"""
        try:
            print(f"🔧 Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            if check:
                sys.exit(1)
            return e

    def check_system_requirements(self):
        """Check if all required system packages are installed"""
        print("🔍 Checking system requirements...")

        requirements = [
            "python3",
            "pip3",
            "nginx",
            "certbot",
            "ufw",
            "git"
        ]

        missing = []
        for req in requirements:
            if not self.run_command(f"which {req}", check=False).returncode == 0:
                missing.append(req)

        if missing:
            print(f"❌ Missing required packages: {', '.join(missing)}")
            print("📦 Installing missing packages...")
            self.run_command("sudo apt update")
            self.run_command(f"sudo apt install -y {' '.join(missing)}")
        else:
            print("✅ All system requirements met")

    def setup_python_environment(self):
        """Set up Python virtual environment and install dependencies"""
        print("🐍 Setting up Python environment...")

        venv_path = self.project_root / 'venv'
        if not venv_path.exists():
            self.run_command("python3 -m venv venv")

        # Activate virtual environment and install dependencies
        pip_path = venv_path / 'bin' / 'pip'
        requirements_file = self.project_root / 'requirements_production.txt'

        if not requirements_file.exists():
            self.create_production_requirements()

        self.run_command(f"{pip_path} install --upgrade pip")
        self.run_command(f"{pip_path} install -r requirements_production.txt")

        print("✅ Python environment ready")

    def create_production_requirements(self):
        """Create production requirements file"""
        requirements = [
            "flask==2.3.3",
            "flask-cors==4.0.0",
            "pandas==2.0.3",
            "numpy==1.24.3",
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "gunicorn==21.2.0",
            "gevent==23.9.1",
            "werkzeug==2.3.7",
            "jinja2==3.1.2",
            "click==8.1.7",
            "itsdangerous==2.1.2",
            "blinker==1.6.2"
        ]

        with open('requirements_production.txt', 'w') as f:
            f.write('\n'.join(requirements))

        print("📝 Created production requirements file")

    def create_nginx_config(self):
        """Create Nginx configuration for both services"""
        print("🌐 Creating Nginx configuration...")

        nginx_config = f"""
# UR Trading Expert Production Configuration
upstream dashboard_app {{
    server 127.0.0.1:{self.config['dashboard_port']};
}}

upstream mobile_app {{
    server 127.0.0.1:{self.config['mobile_port']};
}}

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied expired no-cache no-store private must-revalidate auth;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

# Rate limiting
limit_req_zone $binary_remote_addr zone=dashboard:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=mobile:10m rate=20r/s;

server {{
    listen 80;
    server_name {self.config['domain']};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {self.config['domain']};

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/{self.config['domain']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.config['domain']}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Dashboard API
    location /api/ {{
        limit_req zone=dashboard burst=20 nodelay;
        proxy_pass http://dashboard_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Personal Dashboard Web App
    location /dashboard/ {{
        alias {self.project_root}/personal_trading_dashboard.html;
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }}

    # Mobile App
    location /mobile/ {{
        alias {self.project_root}/URTradingExpertMobile/mobile_app.html;
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }}

    # Static assets with caching
    location /static/ {{
        alias {self.project_root}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""

        nginx_path = Path('/etc/nginx/sites-available/ur-trading-expert')
        with open(nginx_path, 'w') as f:
            f.write(nginx_config)

        # Enable site
        self.run_command("sudo ln -sf /etc/nginx/sites-available/ur-trading-expert /etc/nginx/sites-enabled/")
        self.run_command("sudo nginx -t")
        self.run_command("sudo systemctl reload nginx")

        print("✅ Nginx configuration created and enabled")

    def setup_ssl(self):
        """Set up SSL certificates using Let's Encrypt"""
        if not self.config.get('ssl_auto', True):
            print("⏭️  SSL auto-setup disabled, skipping...")
            return

        print("🔒 Setting up SSL certificates...")

        # Install certbot if not present
        self.run_command("sudo apt install -y certbot python3-certbot-nginx")

        # Get SSL certificate
        domain = self.config['domain']
        email = self.config['email']

        self.run_command(f"sudo certbot --nginx -d {domain} --email {email} --agree-tos --non-interactive")

        # Set up auto-renewal
        self.run_command("sudo crontab -l | {{ cat; echo '0 12 * * * /usr/bin/certbot renew --quiet'; }} | sudo crontab -")

        print("✅ SSL certificates configured")

    def create_systemd_services(self):
        """Create systemd services for both applications"""
        print("⚙️ Creating systemd services...")

        # Dashboard service
        dashboard_service = f"""
[Unit]
Description=UR Trading Expert Personal Dashboard API
After=network.target

[Service]
Type=exec
User={os.getenv('USER')}
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
Environment=PYTHONPATH={self.project_root}
Environment=FLASK_ENV=production
Environment=FLASK_APP=personal_dashboard_api.py
ExecStart={self.project_root}/venv/bin/gunicorn --bind 127.0.0.1:{self.config['dashboard_port']} --workers 3 --worker-class gevent personal_dashboard_api:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dashboard-api

[Install]
WantedBy=multi-user.target
"""

        # Write dashboard service
        with open('/etc/systemd/system/ur-dashboard.service', 'w') as f:
            f.write(dashboard_service)

        print("✅ Systemd services created")

    def setup_firewall(self):
        """Configure UFW firewall"""
        print("🔥 Configuring firewall...")

        self.run_command("sudo ufw --force enable")
        self.run_command("sudo ufw allow OpenSSH")
        self.run_command("sudo ufw allow 'Nginx Full'")
        self.run_command("sudo ufw --force reload")

        print("✅ Firewall configured")

    def create_monitoring_setup(self):
        """Set up basic monitoring and logging"""
        print("📊 Setting up monitoring...")

        # Create log directory
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)

        # Create logrotate configuration
        logrotate_config = f"""
{self.project_root}/logs/*.log {{
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 {os.getenv('USER')} {os.getenv('USER')}
    postrotate
        systemctl reload ur-dashboard.service
    endscript
}}
"""

        with open('/etc/logrotate.d/ur-trading-expert', 'w') as f:
            f.write(logrotate_config)

        print("✅ Monitoring setup completed")

    def create_deployment_script(self):
        """Create a deployment script for easy updates"""
        deploy_script = f"""#!/bin/bash
# UR Trading Expert Deployment Script

echo "🚀 Deploying UR Trading Expert..."

# Navigate to project directory
cd {self.project_root}

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements_production.txt

# Run database migrations if any
echo "🗄️ Running migrations..."
# Add migration commands here if needed

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart ur-dashboard.service
sudo systemctl reload nginx

# Health check
echo "🏥 Running health checks..."
sleep 5
curl -f https://{self.config['domain']}/health || echo "⚠️ Health check failed"

echo "✅ Deployment completed!"
"""

        deploy_path = self.project_root / 'deploy.sh'
        with open(deploy_path, 'w') as f:
            f.write(deploy_script)

        self.run_command("chmod +x deploy.sh")

        print("✅ Deployment script created")

    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting UR Trading Expert Production Deployment")
        print("=" * 50)

        try:
            # Pre-deployment checks
            self.check_system_requirements()
            self.setup_python_environment()

            # Server configuration
            self.create_nginx_config()
            self.create_systemd_services()
            self.setup_firewall()

            # SSL and security
            if self.config.get('ssl_certbot', True):
                self.setup_ssl()

            # Monitoring and maintenance
            if self.config.get('monitoring', True):
                self.create_monitoring_setup()

            self.create_deployment_script()

            # Start services
            print("🎯 Starting services...")
            self.run_command("sudo systemctl daemon-reload")
            self.run_command("sudo systemctl enable ur-dashboard.service")
            self.run_command("sudo systemctl start ur-dashboard.service")
            self.run_command("sudo systemctl enable nginx")
            self.run_command("sudo systemctl restart nginx")

            print("🎉 Deployment completed successfully!")
            print(f"🌐 Your app is now live at: https://{self.config['domain']}")
            print(f"📊 Dashboard API: https://{self.config['domain']}/api/")
            print(f"📱 Mobile App: https://{self.config['domain']}/mobile/")
            print(f"🔄 To deploy updates: ./deploy.sh")

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Deploy UR Trading Expert to production')
    parser.add_argument('--domain', help='Domain name for the application')
    parser.add_argument('--email', help='Email for SSL certificate')
    parser.add_argument('--skip-ssl', action='store_true', help='Skip SSL certificate setup')
    parser.add_argument('--config', help='Path to custom config file')

    args = parser.parse_args()

    deployer = ProductionDeployer()

    # Override config with command line args
    if args.domain:
        deployer.config['domain'] = args.domain
    if args.email:
        deployer.config['email'] = args.email
    if args.skip_ssl:
        deployer.config['ssl_certbot'] = False

    deployer.deploy()

if __name__ == '__main__':
    main()
