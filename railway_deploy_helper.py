#!/usr/bin/env python3
"""
Railway Deployment Helper Script
Automates Railway deployment steps for UR Trading Expert Bot
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def check_railway_cli():
    """Check if Railway CLI is installed and working"""
    return run_command("railway --version", "Checking Railway CLI installation")

def check_python_dependencies():
    """Check if Python dependencies are installed"""
    try:
        import telegram
        import sqlalchemy
        import stripe
        print("✅ Python dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        return False

def create_railway_config():
    """Create railway.json config file if it doesn't exist"""
    config_path = Path("railway.json")
    if not config_path.exists():
        config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "python telegram_bot.py"
            },
            "environments": {
                "production": {
                    "variables": {
                        "LOG_LEVEL": "INFO",
                        "HEALTH_CHECK_ENABLED": "true",
                        "BACKUP_ENABLED": "true"
                    }
                }
            }
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ Created railway.json configuration")
        return True
    else:
        print("✅ railway.json already exists")
        return True

def main():
    print("🚀 UR Trading Expert Bot - Railway Deployment Helper")
    print("=" * 60)

    # Check prerequisites
    print("\n📋 Checking prerequisites...")

    if not check_python_dependencies():
        print("\n❌ Python dependencies missing. Install with:")
        print("pip install -r requirements.txt")
        return False

    # Create Railway config
    if not create_railway_config():
        return False

    # Check Railway CLI
    if not check_railway_cli():
        print("\n❌ Railway CLI not available. Please use Railway web dashboard instead.")
        print("Go to: https://railway.app/dashboard")
        return False

    print("\n🎯 Deployment Steps:")
    print("1. Add PostgreSQL database in Railway dashboard")
    print("2. Set environment variables in Railway dashboard")
    print("3. Deploy service using: railway up")
    print("4. Install dependencies: railway run pip install -r requirements.txt")
    print("5. Run migration: railway run python migrate_to_postgresql.py")
    print("6. Verify service is online")

    # Offer to run deployment
    response = input("\n🚀 Ready to deploy? (y/N): ").lower().strip()
    if response == 'y':
        print("\n📤 Starting deployment...")

        # Link to project (if not already linked)
        run_command("railway link", "Linking to Railway project")

        # Deploy
        if run_command("railway up", "Deploying to Railway"):
            print("\n🎉 Deployment successful!")
            print("📊 Check Railway dashboard for service status")
            print("🔗 Get your app URL from Railway dashboard")
            return True
        else:
            print("\n❌ Deployment failed. Check Railway dashboard for errors.")
            return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)




