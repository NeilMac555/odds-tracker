# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

Before deploying to Railway, ensure:

1. **All files are committed to GitHub:**
   ```bash
   git status  # Check if all files are committed
   git add .
   git commit -m "Fix deployment configuration"
   git push
   ```

2. **Required files exist in repository:**
   - ✅ `Procfile` (must contain: `web: bash start.sh`)
   - ✅ `requirements.txt` (with all dependencies)
   - ✅ `runtime.txt` (Python version)
   - ✅ `start.sh` (executable startup script)
   - ✅ `dashboard.py` (main Streamlit app)
   - ✅ `data_collector.py` (background service)
   - ✅ `init_db.py` (database initialization)

3. **Railway Project Setup:**
   - ✅ Project created on Railway
   - ✅ Connected to GitHub repository
   - ✅ PostgreSQL database added
   - ✅ Environment variables set:
     - `DATABASE_URL` (auto-set by Railway when PostgreSQL is added)
     - `ODDS_API_KEY` (you must set this manually)

## 🔍 Troubleshooting: Nothing Being Deployed

### Issue: Railway shows no deployments

**Check 1: Is Railway connected to your repo?**
1. Go to Railway dashboard
2. Click on your project
3. Go to Settings → Source
4. Verify GitHub repo is connected
5. If not connected: Click "Connect Repo" and select your repository

**Check 2: Is Railway detecting changes?**
- Railway auto-deploys on push to the main/master branch
- Make a small change and push to trigger deployment
- Or manually trigger: Deployments → "Redeploy"

**Check 3: Check for build errors**
1. Go to your service in Railway
2. Click "Deployments" tab
3. Look for any failed builds
4. Check build logs for errors

**Check 4: Verify Procfile is correct**
- Must be exactly: `web: bash start.sh`
- No extra spaces or newlines
- File should be in root directory

**Check 5: Check Railway service status**
- Make sure the service isn't paused
- Service should show "Active" status

## 🚀 Manual Deployment Trigger

If automatic deployment isn't working:

1. **Trigger manual deploy:**
   - Go to Railway → Your Project → Service
   - Click "Deployments" tab
   - Click "Redeploy" on latest deployment

2. **Or make a dummy commit:**
   ```bash
   echo "# Trigger deployment" >> README.md
   git add README.md
   git commit -m "Trigger Railway deployment"
   git push
   ```

## 📋 Quick Verification

Run these checks in Railway dashboard:

- [ ] Service exists and shows "Active"
- [ ] Latest deployment shows status (building/running/failed)
- [ ] Build logs show no errors
- [ ] Runtime logs show app starting
- [ ] Environment variables are set
- [ ] Public URL is generated

## 🔧 If Still Not Working

1. **Delete and recreate the service:**
   - Delete current service in Railway
   - Create new service
   - Connect to same GitHub repo
   - Add PostgreSQL database again
   - Set environment variables

2. **Check Railway status page:**
   - https://status.railway.app
   - Ensure Railway isn't experiencing outages

3. **Verify GitHub connection:**
   - Ensure Railway has access to your repository
   - Check GitHub → Settings → Applications → Railway

4. **Try simplified Procfile:**
   If `bash start.sh` doesn't work, try direct command in Procfile:
   ```
   web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
   ```
   (But this won't start the data collector, so not recommended)

## 💡 Common Issues

**"No deployments found"**
→ Railway hasn't detected your repo yet. Connect it in Settings.

**"Build failed"**
→ Check build logs. Usually missing dependencies or syntax errors.

**"Deployment succeeded but app won't start"**
→ Check runtime logs. Usually missing environment variables or port binding issues.

**"Service not found"**
→ Create a new service and connect your GitHub repo.