@echo off
REM URTRADINGEXPERT.COM - Push to GitHub Batch Script

echo 🚀 Pushing URTRADINGEXPERT.COM to GitHub...
echo.

REM Check if remote is configured
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GitHub remote not configured!
    echo Please run: git remote add origin https://github.com/YOUR_USERNAME/ur-trading-expert.git
    echo Replace YOUR_USERNAME with your actual GitHub username
    goto :error
)

REM Check current branch
for /f %%i in ('git branch --show-current') do set BRANCH=%%i
echo 📋 Current branch: %BRANCH%
echo.

REM Push to GitHub
echo ⬆️ Pushing to GitHub...
git push -u origin %BRANCH%

if %errorlevel% equ 0 (
    echo ✅ Successfully pushed to GitHub!
    echo.
    echo 🌐 Your repository is now live at:
    for /f %%i in ('git remote get-url origin') do (
        REM Convert SSH URL to HTTPS if needed
        set REMOTE_URL=%%i
        set REMOTE_URL=!REMOTE_URL:git@github.com:=https://github.com/!
        echo !REMOTE_URL!
    )
    echo.
    echo 📋 Next steps:
    echo 1. Go to your GitHub repository
    echo 2. Copy the repository URL
    echo 3. Use it for deployment: git clone YOUR_REPO_URL
    echo 4. Set up GitHub Actions for CI/CD (optional)
    echo.
    echo 🎊 Ready to deploy to production!
) else (
    echo ❌ Failed to push to GitHub
    echo.
    echo 🔧 Troubleshooting:
    echo - Check your GitHub credentials
    echo - Verify repository exists and you have access
    echo - Try: git push --force-with-lease origin %BRANCH%
    goto :error
)

goto :eof

:error
echo.
echo 💡 Need help? Check the GITHUB_README.md file for detailed instructions.
pause
exit /b 1
