"""
UR Trading Expert Beta - Quick Setup Script
===========================================

Automated setup for the beta version of UR Trading Expert.

This script will:
1. Check system requirements
2. Install necessary dependencies
3. Set up environment variables
4. Launch the beta application

Requirements:
- Python 3.8+
- Internet connection
- Telegram Bot Token (from @BotFather)

===========================================
Beta Version: 0.9.0
"""

import sys
import os
import subprocess
import importlib.util

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🚀 UR TRADING EXPERT BETA - SETUP")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_telegram_library():
    """Check if telegram library is installed"""
    print("📦 Checking Telegram library...")
    try:
        import telegram
        print(f"✅ python-telegram-bot {telegram.__version__} - OK")
        return True
    except ImportError:
        print("❌ python-telegram-bot not found")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")

    dependencies = [
        "python-telegram-bot",
        "pandas",
        "numpy"
    ]

    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {dep} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False

    return True

def setup_environment():
    """Setup environment variables"""
    print("⚙️  Setting up environment...")

    # Check if token is already set
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token != 'YOUR_BOT_TOKEN_HERE':
        print("✅ Bot token already configured")
        return True

    print()
    print("🤖 Telegram Bot Setup:")
    print("1. Go to Telegram and search for @BotFather")
    print("2. Send /newbot and follow instructions")
    print("3. Copy your bot token (it looks like: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)")
    print()

    while True:
        token = input("Enter your bot token: ").strip()
        if token and len(token) > 45:  # Basic validation
            # Set environment variable
            os.environ['TELEGRAM_BOT_TOKEN'] = token
            print("✅ Bot token configured")
            return True
        else:
            print("❌ Invalid token format. Please try again.")

def test_bot_connection():
    """Test bot connection"""
    print("🤖 Testing bot connection...")

    try:
        from telegram import Bot
        import asyncio

        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ No bot token found")
            return False

        async def test():
            bot = Bot(token)
            info = await bot.get_me()
            return info.username

        username = asyncio.run(test())
        print(f"✅ Bot connected: @{username}")
        return True

    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False

def launch_beta():
    """Launch the beta application"""
    print("🚀 Launching UR Trading Expert Beta...")

    try:
        # Import and run the beta application
        spec = importlib.util.spec_from_file_location("beta_app", "UR_trading_Expert_beta.py")
        beta_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(beta_module)

        # Run the main function
        beta_module.main()

    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Error launching beta: {e}")
        print("💡 Try running: python UR_trading_Expert_beta.py")

def main():
    """Main setup function"""
    print_header()

    # Step 1: Check Python version
    if not check_python_version():
        return

    # Step 2: Check existing installation
    telegram_ok = check_telegram_library()

    # Step 3: Install dependencies if needed
    if not telegram_ok:
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            return

        # Re-check after installation
        if not check_telegram_library():
            print("❌ Dependencies still not available")
            return

    # Step 4: Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return

    # Step 5: Test bot connection
    if not test_bot_connection():
        print("❌ Bot connection test failed")
        print("💡 Double-check your bot token from @BotFather")
        return

    print()
    print("🎉 Setup complete!")
    print("🚀 Starting UR Trading Expert Beta...")
    print("=" * 60)

    # Step 6: Launch beta
    launch_beta()

if __name__ == "__main__":
    main()
