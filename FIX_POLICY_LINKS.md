# 🔧 Fix Terms of Service & Privacy Policy Links

## Problem
The live site at `https://urtradingexpert.com/` is linking to `.md` files that don't exist, causing 404 errors.

## Solution
Upload the updated files to your GitHub Pages repository.

## Files to Upload/Update

### 1. Update `index.html`
- ✅ Already fixed locally (uses `.html` links)
- ⚠️ Needs to be uploaded to GitHub

### 2. Upload Policy Files
Make sure these files are in your GitHub repository root:
- ✅ `terms_of_service.html`
- ✅ `privacy_policy.html`

## Quick Fix Steps

### Option 1: GitHub Web Interface (Easiest)

1. **Go to your GitHub repository** (the one hosting `urtradingexpert.com`)

2. **Upload/Update `index.html`**
   - Click on `index.html` in the repository
   - Click "Edit" (pencil icon)
   - Copy the entire content from your local `index.html` file
   - Paste and replace all content
   - Commit changes with message: "Fix Terms of Service and Privacy Policy links"

3. **Upload Policy Files**
   - Click "Add file" > "Upload files"
   - Drag and drop:
     - `terms_of_service.html`
     - `privacy_policy.html`
   - Commit with message: "Add Terms of Service and Privacy Policy pages"

4. **Wait 1-2 minutes** for GitHub Pages to rebuild

5. **Test the links:**
   - `https://urtradingexpert.com/terms_of_service.html`
   - `https://urtradingexpert.com/privacy_policy.html`

### Option 2: Git Command Line

```bash
# Navigate to your repository
cd /path/to/your/github/repo

# Copy files from your local directory
cp C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\index.html .
cp C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\terms_of_service.html .
cp C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\privacy_policy.html .

# Commit and push
git add index.html terms_of_service.html privacy_policy.html
git commit -m "Fix Terms of Service and Privacy Policy links"
git push origin main
```

## Verify After Upload

1. Visit: `https://urtradingexpert.com/terms_of_service.html` ✅ Should work
2. Visit: `https://urtradingexpert.com/privacy_policy.html` ✅ Should work
3. Click footer links on homepage ✅ Should work

## Current Status

- ✅ Local files are correct
- ✅ `index.html` has proper `.html` links
- ✅ Policy files exist and are formatted correctly
- ⚠️ Need to deploy to GitHub Pages

## Need Help?

If you're not sure which GitHub repository hosts your site:
1. Check your GitHub Pages settings (Settings > Pages)
2. Or check your domain DNS settings to see which GitHub repo it points to


