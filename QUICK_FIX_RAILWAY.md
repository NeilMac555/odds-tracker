# 🚨 Quick Fix: Railway Not Deploying

## Step 1: Commit and Push ALL Files

Make sure ALL files are committed and pushed to GitHub:

```bash
# Check what files need to be committed
git status

# Add all files (including new ones)
git add .

# Commit everything
git commit -m "Fix Railway deployment configuration"

# Push to GitHub
git push origin main
# (or 'git push origin master' if your main branch is called master)
```

**Important files that must be in GitHub:**
- `Procfile`
- `railway.json`
- `nixpacks.toml`
- `start.sh`
- `requirements.txt`
- `runtime.txt`
- All Python files (dashboard.py, data_collector.py, init_db.py, etc.)

## Step 2: Verify Railway Connection

1. **Go to Railway Dashboard:** https://railway.app
2. **Click on your project**
3. **Go to Settings tab**
4. **Check "Source" section:**
   - ✅ Should show your GitHub repository
   - ✅ Should show the branch (usually `main` or `master`)
   - ❌ If it says "Not connected", click "Connect Repo"

## Step 3: Trigger a Deployment

**Option A: Automatic (Recommended)**
- Push any change to GitHub (even a small one)
- Railway should automatically detect and deploy

**Option B: Manual Trigger**
1. In Railway dashboard, go to your service
2. Click "Deployments" tab
3. Click "Redeploy" button on the latest deployment

**Option C: Force by Making a Dummy Commit**
```bash
echo "" >> README.md
git add README.md
git commit -m "Trigger Railway deployment"
git push
```

## Step 4: Check Deployment Status

1. In Railway, go to your **service** (not just the project)
2. Click **"Deployments"** tab
3. You should see a list of deployments with status:
   - 🟡 **Building** = Railway is building your app
   - 🟢 **Success** = App deployed successfully
   - 🔴 **Failed** = Check logs for errors

## Step 5: Check Build Logs

If deployment fails or shows "Building" for a long time:

1. Click on the deployment in "Deployments" tab
2. Look at the build logs
3. Common errors:
   - "Module not found" → Check `requirements.txt`
   - "Command not found" → Check `Procfile` syntax
   - "Port already in use" → Railway handles this automatically

## Step 6: Verify Environment Variables

Even if deployment succeeds, app won't work without:

1. Go to your service → **"Variables"** tab
2. Must have:
   - ✅ `DATABASE_URL` (auto-added when you add PostgreSQL)
   - ✅ `ODDS_API_KEY` (you must add this manually)

**To add ODDS_API_KEY:**
1. Click "+ New Variable"
2. Name: `ODDS_API_KEY`
3. Value: (paste your API key)
4. Click "Add"

## ⚠️ If Still Nothing Happens

**Try deleting and recreating the service:**
1. In Railway, delete your current service
2. Click "+ New" → "GitHub Repo"
3. Select your repository
4. Railway will auto-detect it should use the `Procfile`
5. Add PostgreSQL database
6. Set `ODDS_API_KEY` variable
7. Wait for deployment

**Or check Railway status:**
- Visit https://status.railway.app
- Make sure Railway isn't down

## ✅ Success Indicators

You'll know it's working when:
- ✅ Deployment shows "Success" status
- ✅ Service shows "Active" (green)
- ✅ You get a public URL (in Settings → Domains)
- ✅ Runtime logs show "Starting Streamlit dashboard..."
- ✅ You can visit the URL and see your app

## 🆘 Still Not Working?

Share with me:
1. What you see in Railway "Deployments" tab (screenshot if possible)
2. Any error messages from build logs
3. Whether your files are pushed to GitHub (run `git status` and share output)