#!/bin/bash

# Start data collector in background
python data_collector.py &

# Wait a few seconds for database to initialize
sleep 5

# Start Streamlit dashboard
streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
