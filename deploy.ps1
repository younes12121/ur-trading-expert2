# Production Deployment Script for Windows
# Deploys the trading bot to production

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Trading Bot Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "   Copy .env.example to .env and fill in your values" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green

# Run pre-deployment checklist
Write-Host ""
Write-Host "🔍 Running pre-deployment checks..." -ForegroundColor Cyan
try {
    $checkResult = python pre_deployment_checklist.py --environment production --export 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All pre-deployment checks passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Pre-deployment checks failed!" -ForegroundColor Red
        Write-Host $checkResult -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Pre-deployment checks failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Verify performance mode is enabled
Write-Host ""
Write-Host "⚡ Verifying performance optimizations..." -ForegroundColor Cyan
python -c "
import config
perf_mode = getattr(config, 'PERFORMANCE_MODE', False)
caching = getattr(config, 'ENABLE_CACHING', False)
concurrent = getattr(config, 'CONCURRENT_API', False)

print(f'   Performance Mode: {\"ENABLED\" if perf_mode else \"DISABLED\"}')
print(f'   Caching: {\"ENABLED\" if caching else \"DISABLED\"}')
print(f'   Concurrent API: {\"ENABLED\" if concurrent else \"DISABLED\"}')

if not perf_mode:
    print('ERROR: Performance mode must be enabled for production!')
    exit(1)
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Performance mode verification failed!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Run database migration (if needed)
Write-Host ""
$runMigration = Read-Host "Run database migration? (y/n)"
if ($runMigration -eq "y" -or $runMigration -eq "Y") {
    Write-Host "🔄 Running database migration..." -ForegroundColor Cyan
    python migrate_to_postgresql.py --backup
}

# Run security audit
Write-Host ""
$runAudit = Read-Host "Run security audit? (y/n)"
if ($runAudit -eq "y" -or $runAudit -eq "Y") {
    Write-Host "🔒 Running security audit..." -ForegroundColor Cyan
    python security_audit.py
}

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "backups" | Out-Null

# Run comprehensive health check
Write-Host ""
Write-Host "🏥 Running comprehensive health check..." -ForegroundColor Cyan
python health_check.py --comprehensive

# Start monitoring services
Write-Host ""
Write-Host "📊 Starting monitoring services..." -ForegroundColor Cyan
Write-Host "   Starting performance dashboard..." -ForegroundColor White
Start-Process python -ArgumentList "performance_dashboard.py --web" -NoNewWindow
Write-Host "   Starting performance alerts..." -ForegroundColor White
Start-Process python -ArgumentList "performance_alerts.py" -NoNewWindow
Write-Host "   Starting production monitoring..." -ForegroundColor White
Start-Process python -ArgumentList "production_monitoring.py" -NoNewWindow

Write-Host "✅ Monitoring services started!" -ForegroundColor Green

# Health check
Write-Host ""
Write-Host "🏥 Running final health check..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Health check passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Health check endpoint not responding (this is OK if bot isn't running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Monitor logs: Get-Content logs\app.log -Wait" -ForegroundColor White
Write-Host "2. Check health: Invoke-WebRequest http://localhost:8080/health" -ForegroundColor White
Write-Host "3. Test bot: Send /start to your bot on Telegram" -ForegroundColor White
Write-Host "4. Set up backups: python backup_system.py" -ForegroundColor White
Write-Host ""

