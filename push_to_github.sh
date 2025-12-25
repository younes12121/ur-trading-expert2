#!/bin/bash
# URTRADINGEXPERT.COM - Push to GitHub Script

echo "🚀 Pushing URTRADINGEXPERT.COM to GitHub..."

# Check if remote is configured
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ GitHub remote not configured!"
    echo "Please run: git remote add origin https://github.com/YOUR_USERNAME/ur-trading-expert.git"
    echo "Replace YOUR_USERNAME with your actual GitHub username"
    exit 1
fi

# Check current branch
BRANCH=$(git branch --show-current)
echo "📋 Current branch: $BRANCH"

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push -u origin $BRANCH

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 Your repository is now live at:"
    REMOTE_URL=$(git remote get-url origin)
    # Convert SSH URL to HTTPS if needed
    REMOTE_URL=$(echo $REMOTE_URL | sed 's|git@github.com:|https://github.com/|')
    echo "$REMOTE_URL"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to your GitHub repository"
    echo "2. Copy the repository URL"
    echo "3. Use it for deployment: git clone YOUR_REPO_URL"
    echo "4. Set up GitHub Actions for CI/CD (optional)"
    echo ""
    echo "🎊 Ready to deploy to production!"
else
    echo "❌ Failed to push to GitHub"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- Check your GitHub credentials"
    echo "- Verify repository exists and you have access"
    echo "- Try: git push --force-with-lease origin $BRANCH"
fi
