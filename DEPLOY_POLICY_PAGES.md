# 🚀 How to Add Terms of Service & Privacy Policy to Your Live Site

Your site is hosted on **GitHub Pages** at `https://urtradingexpert.com/`. Here's how to add the policy pages:

---

## Method 1: GitHub Web Interface (Easiest - No Git Required) ⭐

### Step 1: Go to Your GitHub Repository
1. Open your browser and go to **github.com**
2. Log in to your account
3. Find the repository that hosts your website (the one connected to `urtradingexpert.com`)
   - Usually named something like `urtradingexpert`, `landing-page`, or similar
   - Check your GitHub Pages settings if unsure

### Step 2: Upload the Files
1. **Click "Add file"** button (top right of the repository page)
2. **Select "Upload files"**
3. **Drag and drop** these two files into the upload area:
   - `terms_of_service.html`
   - `privacy_policy.html`
4. **Scroll down** and click **"Commit changes"**
5. **Add a commit message**: "Add Terms of Service and Privacy Policy pages"
6. **Click "Commit changes"**

### Step 3: Wait for GitHub Pages to Update
- GitHub Pages usually updates within **1-2 minutes**
- You can check the status in: **Settings > Pages** (look for the green checkmark)

### Step 4: Test Your Pages
Visit these URLs to verify they work:
- ✅ `https://urtradingexpert.com/terms_of_service.html`
- ✅ `https://urtradingexpert.com/privacy_policy.html`

---

## Method 2: Using Git Command Line (If You Have Git Installed)

### Step 1: Navigate to Your Repository
```bash
cd /path/to/your/github/repo
```

### Step 2: Copy Files to Repository
```bash
# Copy the files from your local directory to the repo
cp "C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\terms_of_service.html" .
cp "C:\Users\lenovo\.gemini\antigravity\scratch\smc_trading_analysis\backtesting\privacy_policy.html" .
```

### Step 3: Commit and Push
```bash
git add terms_of_service.html privacy_policy.html
git commit -m "Add Terms of Service and Privacy Policy pages"
git push origin main
```

---

## Method 3: Using GitHub Desktop (If You Have It)

1. **Open GitHub Desktop**
2. **Select your repository**
3. **Drag the files** into the repository folder
4. **Commit** with message: "Add Terms of Service and Privacy Policy pages"
5. **Push** to GitHub

---

## ✅ Verification Checklist

After uploading, verify:

- [ ] Files appear in your GitHub repository
- [ ] `https://urtradingexpert.com/terms_of_service.html` loads correctly
- [ ] `https://urtradingexpert.com/privacy_policy.html` loads correctly
- [ ] Footer links on homepage work
- [ ] Pages match your site's branding (dark theme, same header/footer)
- [ ] Mobile view looks good

---

## 🔍 Finding Your Repository

If you're not sure which repository hosts your site:

1. Go to **github.com** and log in
2. Click your **profile picture** (top right)
3. Click **"Your repositories"**
4. Look for repositories that might contain your website
5. Check the repository's **Settings > Pages** to see if it's connected to `urtradingexpert.com`

Or check your domain DNS settings to see which GitHub repository it points to.

---

## 🐛 Troubleshooting

### Issue: "404 Not Found" after uploading
**Solution:**
- Wait 2-3 minutes for GitHub Pages to rebuild
- Clear your browser cache
- Check that files are in the **root directory** of the repository (not in a subfolder)

### Issue: Files uploaded but site not updating
**Solution:**
- Go to **Settings > Pages** in your repository
- Check if there are any build errors
- Try making a small change to trigger a rebuild

### Issue: Can't find the repository
**Solution:**
- Check your email for GitHub notifications about the repository
- Look in your GitHub organizations (if you created it under an org)
- Check if someone else created the repository

---

## 📝 Quick Reference

**Files to upload:**
- `terms_of_service.html`
- `privacy_policy.html`

**Where to upload:**
- Root directory of your GitHub Pages repository

**Expected URLs after upload:**
- `https://urtradingexpert.com/terms_of_service.html`
- `https://urtradingexpert.com/privacy_policy.html`

---

## 🎯 Next Steps After Upload

1. ✅ Test both pages load correctly
2. ✅ Click footer links on homepage to verify navigation
3. ✅ Test on mobile device
4. ✅ Share with team/stakeholders for review

---

**Need help?** If you can't find your repository or run into issues, let me know and I can help troubleshoot!




