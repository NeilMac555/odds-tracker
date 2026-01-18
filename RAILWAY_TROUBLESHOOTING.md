# Railway Deployment Troubleshooting Guide

## Issues Fixed

1. ✅ Added `railway.json` configuration file for better Railway detection
2. ✅ Fixed missing `commence_time` column in database schema
3. ✅ Improved `start.sh` with better logging and error handling

## What to Check in Railway Dashboard

### 1. Check if Service is Detected
- Go to your Railway project dashboard
- You should see a service called "odds-tracker" or similar
- If you don't see any service, Railway might not have detected your repo

### 2. Check Build Logs
- Click on your service
- Go to the "Deployments" tab
- Click on the most recent deployment
- Look for build errors in the logs

**Common build errors:**
- Missing dependencies (check `requirements.txt`)
- Python version issues (check `runtime.txt`)
- Database connection errors (check `DATABASE_URL` environment variable)

### 3. Check Runtime Logs
- Go to the "Logs" tab in your service
- Look for error messages when the app starts

**Common runtime errors:**
- `DATABASE_URL` not set → Add PostgreSQL database and ensure variable is set
- `ODDS_API_KEY` not set → Add this environment variable manually
- Port binding errors → Railway automatically sets `PORT` variable
- Database schema errors → Should be fixed now with updated `init_db.py`

### 4. Verify Environment Variables
Go to your service → "Variables" tab and ensure:
- ✅ `DATABASE_URL` - Should be auto-added when you add PostgreSQL
- ✅ `ODDS_API_KEY` - You need to add this manually with your API key
- ✅ `PORT` - Railway sets this automatically, don't override it

### 5. Check Service Status
- Green status = Running
- Yellow/Red status = Error - check logs

### 6. Verify Deployment Source
- Go to service → "Settings" tab
- Check "Source" section
- Ensure it's connected to the correct GitHub repo and branch
- If not connected, click "Connect Repo"

## Quick Fixes

### If deployment is not starting:
1. **Trigger manual redeploy:**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment

2. **Check Procfile:**
   - Should contain: `web: bash start.sh`
   - If missing, Railway might not know how to start your app

3. **Verify files are committed:**
   - Make sure `railway.json`, `Procfile`, `start.sh`, `requirements.txt`, and `runtime.txt` are all committed to your GitHub repo

### If app crashes on startup:
1. **Check database connection:**
   - Ensure PostgreSQL service is running
   - Verify `DATABASE_URL` is set correctly

2. **Check API key:**
   - Verify `ODDS_API_KEY` is set
   - Ensure the key is valid

3. **Check logs for specific errors:**
   - Railway logs will show the exact error
   - Common: missing dependencies, import errors, connection timeouts

## Still Not Working?

If you're still having issues:
1. Check the Railway logs (most important!)
2. Share the error messages you see
3. Verify all files are pushed to GitHub
4. Make sure you've added both environment variables (`DATABASE_URL` and `ODDS_API_KEY`)

## Testing Locally

Before deploying, test locally:
```bash
# Set environment variables
export DATABASE_URL="your_database_url"
export ODDS_API_KEY="your_api_key"

# Run the start script
bash start.sh
```

This will help identify any issues before deploying to Railway.