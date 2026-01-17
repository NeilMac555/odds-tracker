#!/bin/bash

# Exit on any error
set -e

# Use Railway's PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

# Initialize database first (ignore errors if already initialized)
python init_db.py || true

# Start data collector in background
python data_collector.py &

# Wait for first odds collection
sleep 10

# Start Streamlit dashboard
streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
