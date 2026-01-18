# 🚂 Railway Deployment Guide - Step by Step

Your code is now on GitHub! Follow these simple steps to deploy to Railway:

## Step 1: Go to Railway
1. Open your web browser
2. Go to: **https://railway.app**
3. Click **"Login"** or **"Sign Up"** (use GitHub to sign in - it's easiest!)

## Step 2: Create New Project
1. Once logged in, click the **"New Project"** button (big green button)
2. Select **"Deploy from GitHub repo"**
3. You'll see a list of your GitHub repositories
4. Find and click on **"odds-tracker"**
5. Railway will start deploying automatically!

## Step 3: Add Database
1. In your Railway project dashboard, click the **"+ New"** button
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will automatically create a PostgreSQL database
5. **Important:** Railway will automatically add the `DATABASE_URL` environment variable - you don't need to do anything!

## Step 4: Add Your API Key
1. In your Railway project, click on your **service** (the one that says "odds-tracker")
2. Go to the **"Variables"** tab
3. Click **"+ New Variable"**
4. Add this variable:
   - **Name:** `ODDS_API_KEY`
   - **Value:** (paste your Odds API key here)
5. Click **"Add"**

## Step 5: Wait for Deployment
1. Railway will automatically:
   - Install all dependencies
   - Run your app
   - Give you a public URL
2. You'll see build logs - wait until it says "Deployed successfully"
3. Click on the **"Settings"** tab
4. Scroll down to **"Domains"**
5. Railway will show you a public URL like: `https://your-app-name.up.railway.app`
6. **Click that URL** to see your app!

## That's It! 🎉

Your app should now be live online. The data collector will start running automatically and collecting odds data.

---

## Troubleshooting

**If something goes wrong:**
1. Check the **"Deployments"** tab for error messages
2. Make sure both environment variables are set:
   - `DATABASE_URL` (should be auto-added when you add PostgreSQL)
   - `ODDS_API_KEY` (you need to add this manually)
3. Check the logs in the Railway dashboard

**Need help?** Share any error messages you see and I can help fix them!
