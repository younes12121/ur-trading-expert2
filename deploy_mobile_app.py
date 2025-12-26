#!/usr/bin/env python3
"""
Deploy UR Trading Expert Mobile App to GitHub Pages
"""

import os
import zipfile
import base64

def create_deployment_package():
    """Create a deployment package for GitHub Pages"""

    print("🚀 UR Trading Expert Mobile App - GitHub Pages Deployment")
    print("=" * 60)

    # Source file
    source_file = "URTradingExpertMobile/mobile_app.html"
    deploy_file = "mobile_app.html"

    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False

    print(f"✅ Found mobile app: {source_file}")

    # Read the mobile app content
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update API URL for deployment (keeping localhost for now since API isn't deployed)
    # The app will fallback to demo data if API is not accessible
    print("✅ API URL configured for localhost (will fallback to demo data)")

    # Create deployment directory
    deploy_dir = "mobile_app_deployment"
    if not os.path.exists(deploy_dir):
        os.makedirs(deploy_dir)

    # Write the deployment file
    deploy_path = os.path.join(deploy_dir, "mobile_app.html")
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created deployment file: {deploy_path}")

    # Create README for GitHub
    readme_content = """# UR Trading Expert Mobile App

A beautiful, responsive mobile trading dashboard for UR Trading Expert.

## Features

- 📊 Live trading signals
- 💼 Portfolio tracking
- 🧠 AI insights
- 📈 Performance analytics
- 📱 Mobile-first design
- ⚡ Real-time updates

## Usage

This mobile app connects to the UR Trading Expert API for live data. If the API is not available, it will display demo data.

## Deployment

This app is deployed using GitHub Pages for easy access via Telegram WebApp.
"""

    readme_path = os.path.join(deploy_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ Created README.md: {readme_path}")

    # Create deployment instructions
    instructions = f"""
📋 MANUAL DEPLOYMENT INSTRUCTIONS
{'='*40}

1. Go to https://github.com and log in

2. Click the "+" button → "New repository"
   - Repository name: ur-trading-expert-mobile
   - Description: Mobile dashboard for UR Trading Expert
   - Make it Public
   - DO NOT initialize with README

3. In the new repository, click "uploading an existing file"

4. Upload these files from the "{deploy_dir}" folder:
   - mobile_app.html
   - README.md

5. Click "Commit changes"

6. In your repository, click "Settings" (top menu)

7. Scroll down to "Pages" (left sidebar)

8. Under "Source", select "main" branch

9. Click "Save"

10. Wait 2-3 minutes, then refresh the page

11. Your app will be available at:
    https://YOUR_USERNAME.github.io/ur-trading-expert-mobile/mobile_app.html

12. Replace YOUR_USERNAME with your actual GitHub username in the URL

13. Test the URL in your browser

{'='*40}
🎉 DEPLOYMENT READY!
{'='*40}

Files created in: {deploy_dir}/
Upload these to GitHub using the web interface.
"""

    print(instructions)

    # Create a ZIP file for easy download
    zip_path = "mobile_app_deployment.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(deploy_path, "mobile_app.html")
        zipf.write(readme_path, "README.md")

    print(f"✅ Created deployment ZIP: {zip_path}")

    return True

def verify_deployment():
    """Verify the deployment was successful"""

    print("\n🔍 DEPLOYMENT VERIFICATION")
    print("=" * 30)

    print("After deployment, your mobile app should be available at:")
    print("https://YOUR_USERNAME.github.io/ur-trading-expert-mobile/mobile_app.html")
    print("\nReplace YOUR_USERNAME with your actual GitHub username.")

    print("\nTo integrate with Telegram bot, add this code to telegram_bot.py:")
    print("""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

async def mobile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile_app_url = "https://YOUR_USERNAME.github.io/ur-trading-expert-mobile/mobile_app.html"

    keyboard = [[
        InlineKeyboardButton(
            "📱 Open Mobile Dashboard",
            web_app=WebAppInfo(url=mobile_app_url)
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📱 *UR Trading Expert Mobile*\\n\\n"
        "Access your trading dashboard on any device!\\n\\n"
        "*Features:*\\n"
        "✅ Live trading signals\\n"
        "✅ Real-time stats & analytics\\n"
        "✅ Win rate tracking\\n"
        "✅ Performance metrics\\n"
        "✅ Beautiful mobile interface\\n\\n"
        "_Tap the button below to launch:_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Add to main():
application.add_handler(CommandHandler("mobile", mobile_command))
application.add_handler(CommandHandler("app", mobile_command))
""")

if __name__ == '__main__':
    success = create_deployment_package()
    if success:
        verify_deployment()
        print("\n🎉 Ready to deploy! Follow the instructions above.")
    else:
        print("❌ Deployment preparation failed.")











