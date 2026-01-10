#!/bin/bash

# Start data collector in background
python data_collector.py &

# Wait a few seconds for database to initialize
sleep 5

# Start Streamlit dashboard on port 8080
streamlit run dashboard.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true
