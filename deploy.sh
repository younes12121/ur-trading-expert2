#!/bin/bash
# Production Deployment Script
# Deploys the trading bot to production

set -e  # Exit on error

echo "=========================================="
echo "🚀 Trading Bot Deployment Script"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Copy .env.example to .env and fill in your values"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Run pre-deployment checklist
echo ""
echo "🔍 Running pre-deployment checks..."
if python3 pre_deployment_checklist.py --environment production; then
    echo "✅ All pre-deployment checks passed!"
else
    echo "❌ Pre-deployment checks failed!"
    echo "   Please fix the issues above before deploying."
    exit 1
fi

# Verify performance mode is enabled
echo ""
echo "⚡ Verifying performance optimizations..."
python3 -c "
import config
perf_mode = getattr(config, 'PERFORMANCE_MODE', False)
caching = getattr(config, 'ENABLE_CACHING', False)
concurrent = getattr(config, 'CONCURRENT_API', False)

print(f'   Performance Mode: {\"✅ ENABLED\" if perf_mode else \"❌ DISABLED\"}')
print(f'   Caching: {\"✅ ENABLED\" if caching else \"❌ DISABLED\"}')
print(f'   Concurrent API: {\"✅ ENABLED\" if concurrent else \"❌ DISABLED\"}')

if not perf_mode:
    echo '❌ Performance mode must be enabled for production!'
    exit 1
fi
"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Run database migration (if needed)
echo ""
read -p "Run database migration? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Running database migration..."
    python3 migrate_to_postgresql.py --backup
fi

# Run security audit
echo ""
read -p "Run security audit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔒 Running security audit..."
    python3 security_audit.py
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs data backups

# Set permissions
echo ""
echo "🔐 Setting permissions..."
chmod 600 .env
chmod 755 *.py

# Start services (if using Docker)
if [ -f docker-compose.yml ]; then
    echo ""
    read -p "Start with Docker Compose? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐳 Starting Docker containers..."
        docker-compose up -d
        echo "✅ Services started!"
        echo "   Check status: docker-compose ps"
        echo "   View logs: docker-compose logs -f"
    fi
fi

# Or start with systemd
if [ -f /etc/systemd/system/trading-bot.service ]; then
    echo ""
    read -p "Start with systemd? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⚙️  Starting systemd service..."
        sudo systemctl start trading-bot
        sudo systemctl enable trading-bot
        echo "✅ Service started!"
        echo "   Check status: sudo systemctl status trading-bot"
    fi
fi

# Run comprehensive health check
echo ""
echo "🏥 Running comprehensive health check..."
python3 health_check.py --comprehensive

# Start monitoring services
echo ""
echo "📊 Starting monitoring services..."
echo "   Starting performance dashboard..."
python3 performance_dashboard.py --web &
echo "   Starting performance alerts..."
python3 performance_alerts.py &
echo "   Starting production monitoring..."
python3 production_monitoring.py &

echo "✅ Monitoring services started!"

# Health check
echo ""
echo "🏥 Running final health check..."
sleep 10
if command -v curl &> /dev/null; then
    curl -f http://localhost:8080/health || echo "⚠️  Health check endpoint not responding"
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Monitor logs: tail -f logs/app.log"
echo "2. Check health: curl http://localhost:8080/health"
echo "3. Test bot: Send /start to your bot on Telegram"
echo "4. Set up backups: python3 backup_system.py"
echo ""

