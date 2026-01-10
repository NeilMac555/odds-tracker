#!/bin/bash

# Initialize database first
python init_db.py

# Start data collector in background
python data_collector.py &

# Wait for first odds collection
sleep 10

# Start Streamlit dashboard on port 8080
streamlit run dashboard.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true
