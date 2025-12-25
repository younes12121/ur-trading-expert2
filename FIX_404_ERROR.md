# 🔧 Fix 404 Error for Privacy Policy & Terms of Service

## Common Causes of 404 Errors on GitHub Pages

### 1. **Case Sensitivity Issue** ⚠️ MOST COMMON
GitHub Pages is **case-sensitive**. The file name must match the URL exactly.

**Check:**
- File in repository: `privacy_policy.html` ✅ (lowercase)
- URL: `privacy_policy.html` ✅ (lowercase)
- File in repository: `Privacy_Policy.html` ❌ (uppercase) - This will cause 404!

### 2. **File Not in Root Directory**
Files must be in the **root directory** (same folder as `index.html`), not in a subfolder.

### 3. **GitHub Pages Still Building**
Sometimes it takes 2-5 minutes for changes to appear.

---

## ✅ Quick Fix Steps

### Step 1: Verify File Names in GitHub
1. Go to: `https://github.com/younes12121/UR-Trading-Expert-Landing`
2. Check the file list - you should see:
   - `privacy_policy.html` (all lowercase)
   - `terms_of_service.html` (all lowercase)

### Step 2: Check File Names Match Exactly
The files must be named **exactly**:
- `privacy_policy.html` (lowercase, with underscore)
- `terms_of_service.html` (lowercase, with underscore)

**NOT:**
- `Privacy_Policy.html` ❌
- `privacy-policy.html` ❌
- `PrivacyPolicy.html` ❌

### Step 3: Verify Files Are in Root Directory
Files should be in the same folder as `index.html`:
```
Repository Root/
├── index.html
├── privacy_policy.html  ← Should be here
├── terms_of_service.html ← Should be here
├── CNAME
└── README
```

### Step 4: Force GitHub Pages Rebuild
1. Go to your repository
2. Click **"Actions"** tab
3. Check if there's a build in progress
4. If needed, make a small change to trigger rebuild:
   - Edit `index.html` (add a space)
   - Commit the change
   - This will trigger a new build

### Step 5: Clear Browser Cache
- Press **Ctrl + Shift + R** (Windows) or **Cmd + Shift + R** (Mac)
- Or try in **Incognito/Private mode**

---

## 🔍 Detailed Troubleshooting

### Check 1: Verify File Names
In your GitHub repository, the files should be named:
- ✅ `privacy_policy.html` (all lowercase)
- ✅ `terms_of_service.html` (all lowercase)

### Check 2: Test Direct URLs
Try these exact URLs:
- `https://urtradingexpert.com/privacy_policy.html`
- `https://urtradingexpert.com/terms_of_service.html`

### Check 3: Check GitHub Pages Build Status
1. Go to: **Settings > Pages**
2. Look for build status
3. Check **Actions** tab for any build errors

### Check 4: Verify Links in index.html
The links in your `index.html` should be:
```html
<a href="privacy_policy.html">Privacy Policy</a>
<a href="terms_of_service.html">Terms of Service</a>
```

---

## 🚨 If Files Have Wrong Case

If your files are named with wrong case (e.g., `Privacy_Policy.html`):

### Option 1: Rename in GitHub
1. Click on the file in GitHub
2. Click the **pencil icon** (Edit)
3. In the filename field, change to lowercase
4. Commit changes

### Option 2: Delete and Re-upload
1. Delete the incorrectly named file
2. Upload the correctly named file (`privacy_policy.html`)

---

## ⏱️ Wait Time

GitHub Pages can take:
- **1-2 minutes** for normal updates
- **Up to 5 minutes** after first upload
- **Up to 10 minutes** if there's a build error

---

## 🧪 Test Checklist

After fixing, test:
- [ ] `https://urtradingexpert.com/privacy_policy.html` loads
- [ ] `https://urtradingexpert.com/terms_of_service.html` loads
- [ ] Footer links on homepage work
- [ ] Pages show dark theme (not 404)
- [ ] Header and footer appear correctly

---

## 💡 Still Not Working?

If you've tried everything:
1. Check **Actions** tab for build errors
2. Verify files are in root directory (not in a subfolder)
3. Make sure file extensions are `.html` (not `.HTML` or `.htm`)
4. Try accessing via the GitHub Pages URL first:
   - `https://younes12121.github.io/UR-Trading-Expert-Landing/privacy_policy.html`
   - If this works, it's a custom domain issue
   - If this doesn't work, it's a file naming/location issue




