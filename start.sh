#!/bin/bash

# Exit on any error (but allow database init to fail)
set -e

# Use Railway's PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

echo "🚀 Starting OddsTracker on port $PORT..."

# Initialize database first (ignore errors if already initialized)
echo "📊 Initializing database..."
python init_db.py || echo "⚠️ Database initialization warning (may already exist)"

# Start data collector in background
echo "🔄 Starting data collector in background..."
nohup python data_collector.py > collector.log 2>&1 &

# Wait a moment for collector to start
sleep 3

# Start Streamlit dashboard (foreground process)
echo "🌐 Starting Streamlit dashboard..."
streamlit run dashboard.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
