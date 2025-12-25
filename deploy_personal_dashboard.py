#!/usr/bin/env python3
"""
Personal Trading Dashboard Deployment Script
Deploy the dashboard as a standalone web application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        print("Flask dependencies found")
        return True
    except ImportError:
        print("Flask not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
            print("Flask installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install Flask")
            return False

def create_deployment_structure():
    """Create deployment directory structure"""
    deployment_dir = Path("personal_dashboard_deployment")
    deployment_dir.mkdir(exist_ok=True)

    # Copy necessary files
    files_to_copy = [
        "personal_trading_dashboard.html",
        "personal_dashboard_api.py",
        "PERSONAL_DASHBOARD_README.md"
    ]

    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, deployment_dir)
            print(f"Copied {file}")

    # Create templates directory for Flask
    templates_dir = deployment_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    shutil.copy("personal_trading_dashboard.html", templates_dir / "personal_trading_dashboard.html")
    print("Created templates directory")

    # Create static data files (copy existing data files if they exist)
    data_files = ["signals_db.json", "user_profiles.json", "trade_history.json"]
    for data_file in data_files:
        if os.path.exists(data_file):
            shutil.copy(data_file, deployment_dir)
            print(f"✅ Copied {data_file}")

    return deployment_dir

def create_startup_script(deployment_dir):
    """Create startup script for the dashboard"""
    startup_script = deployment_dir / "start_dashboard.bat" if os.name == 'nt' else deployment_dir / "start_dashboard.sh"

    if os.name == 'nt':
        # Windows batch script
        script_content = '''@echo off
echo ========================================
echo   Personal Trading Dashboard
echo ========================================
echo.
echo Starting Flask API server...
echo Dashboard will be available at: http://localhost:5001
echo.
python personal_dashboard_api.py
pause
'''
    else:
        # Unix shell script
        script_content = '''#!/bin/bash
echo "========================================"
echo "  Personal Trading Dashboard"
echo "========================================"
echo ""
echo "Starting Flask API server..."
echo "Dashboard will be available at: http://localhost:5001"
echo ""
python3 personal_dashboard_api.py
'''

    with open(startup_script, 'w') as f:
        f.write(script_content)

    if os.name != 'nt':
        os.chmod(startup_script, 0o755)

    print(f"Created startup script: {startup_script}")

def create_requirements_file(deployment_dir):
    """Create requirements.txt for the deployment"""
    requirements = deployment_dir / "requirements.txt"
    with open(requirements, 'w') as f:
        f.write("""Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
""")

    print("Created requirements.txt")

def create_deployment_readme(deployment_dir):
    """Create deployment-specific README"""
    readme_content = f'''# Personal Trading Dashboard - Deployment

## 🚀 Quick Start

### Option 1: Run with Mock Data (Easiest)
1. Open `personal_trading_dashboard.html` directly in your web browser
2. All features work with sample data for demonstration

### Option 2: Run with Live API Server
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the dashboard:
   - **Windows**: Double-click `start_dashboard.bat`
   - **Mac/Linux**: Run `./start_dashboard.sh` or `python3 personal_dashboard_api.py`

3. Open your browser to: http://localhost:5001

## 📁 Files Included

- `personal_trading_dashboard.html` - Main dashboard interface
- `personal_dashboard_api.py` - Flask API server
- `PERSONAL_DASHBOARD_README.md` - Complete documentation
- `requirements.txt` - Python dependencies
- `start_dashboard.bat` / `start_dashboard.sh` - Startup scripts

## 🔗 Data Integration

The dashboard automatically connects to your telegram bot data:

- `signals_db.json` - Live trading signals
- `user_profiles.json` - Portfolio and user data
- `trade_history.json` - Historical trading records

Place these files in the same directory as the API server for live data integration.

## 🌐 Accessing the Dashboard

- **Local Access**: http://localhost:5001
- **Network Access**: Replace `localhost` with your computer's IP address
- **Direct HTML**: Open `personal_trading_dashboard.html` for offline demo

## 🔧 Troubleshooting

### Server won't start
- Ensure Python 3.7+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check that port 5001 is not in use by another application

### Dashboard shows no data
- The dashboard works with mock data by default
- For live data, ensure your bot's data files are in the same directory
- Check browser console for API connection errors

### Performance issues
- The dashboard auto-refreshes every 30 seconds
- Reduce refresh frequency by modifying the JavaScript in the HTML file
- Close the browser tab when not in use to free resources

## 📞 Support

This is a personal trading dashboard for monitoring your trading performance.
It integrates with your existing telegram bot infrastructure.

For questions or issues, check the main README file for detailed documentation.
'''

    readme_path = deployment_dir / "DEPLOYMENT_README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print("✅ Created deployment README")

def main():
    """Main deployment function"""
    print("Personal Trading Dashboard Deployment")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install Flask manually.")
        return False

    # Create deployment structure
    print("\n📁 Creating deployment structure...")
    deployment_dir = create_deployment_structure()

    # Create additional deployment files
    print("\n📄 Creating deployment files...")
    create_startup_script(deployment_dir)
    create_requirements_file(deployment_dir)
    create_deployment_readme(deployment_dir)

    print(f"\n✅ Deployment complete! Files are in: {deployment_dir}")
    print("\n🎯 To start your dashboard:")
    if os.name == 'nt':
        print(f"   1. Go to {deployment_dir}")
        print("   2. Double-click start_dashboard.bat")
    else:
        print(f"   1. cd {deployment_dir}")
        print("   2. ./start_dashboard.sh")
    print("   3. Open http://localhost:5001 in your browser")

    print("\n📖 For detailed instructions, see DEPLOYMENT_README.md")

    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Deployment successful! Your personal trading dashboard is ready.")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)
