import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration with custom favicon
st.set_page_config(
    page_title="OddsEdge - Live Odds Tracker",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E5266;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6E8898;
        margin-bottom: 2rem;
    }
    .move-summary-line1 {
        font-size: 1.05em;
        font-weight: 500;
        line-height: 1.4;
    }
    .move-summary-line2 {
        font-size: 0.9em;
        color: #9CA3AF;
        line-height: 1.3;
        margin-top: 2px;
    }
    .live-indicator {
        background-color: #DC2626;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85em;
        display: inline-block;
        margin-bottom: 8px;
        animation: flash 1.5s infinite;
        float: right;
        margin-top: 0;
    }
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">⚽ OddsEdge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time Soccer Betting Odds Tracker</p>', unsafe_allow_html=True)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    st.error("Database connection not configured")
    st.stop()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def load_latest_odds():
    """Load the most recent odds for each match"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT league, home_team, away_team, bookmaker, home_odds, away_odds, draw_odds, timestamp, commence_time
    FROM (
        SELECT *, 
               ROW_NUMBER() OVER (
                   PARTITION BY league, home_team, away_team, bookmaker 
                   ORDER BY timestamp DESC
               ) as rn
        FROM odds
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
          AND (
              commence_time IS NOT NULL 
              AND commence_time >= CURRENT_DATE 
              AND commence_time < CURRENT_DATE + INTERVAL '3 days'
          )
    ) ranked
    WHERE rn = 1
    ORDER BY league, home_team, bookmaker
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def load_odds_history(league, home_team, away_team, hours=24):
    """Load historical odds for a specific match"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT bookmaker, home_odds, away_odds, draw_odds, timestamp
    FROM odds
    WHERE league = %s 
        AND home_team = %s 
        AND away_team = %s
        AND timestamp >= NOW() - INTERVAL '%s hours'
    ORDER BY timestamp ASC
    """
    
    cursor.execute(query, (league, home_team, away_team, hours))
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_odds_direction(history, odds_type):
    """Calculate odds movement direction"""
    if len(history) < 2:
        return None, None
    
    first_value = history[0][odds_type]
    last_value = history[-1][odds_type]
    
    if last_value > first_value:
        return "↑", "green"
    elif last_value < first_value:
        return "↓", "red"
    else:
        return "—", "gray"

def calculate_no_vig_probabilities(home_odds, draw_odds, away_odds):
    """Calculate no-vig implied probabilities from odds"""
    # Implied probabilities
    home_prob = 1.0 / home_odds
    draw_prob = 1.0 / draw_odds
    away_prob = 1.0 / away_odds
    
    # Total implied probability (includes vig)
    total = home_prob + draw_prob + away_prob
    
    # Remove vig by normalizing
    home_no_vig = home_prob / total
    draw_no_vig = draw_prob / total
    away_no_vig = away_prob / total
    
    return home_no_vig, draw_no_vig, away_no_vig

def get_match_movement_summary(league, home_team, away_team):
    """Get open and current odds with movement summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all odds for this match in last 24h, ordered by timestamp
    query = """
    SELECT home_odds, draw_odds, away_odds, timestamp
    FROM odds
    WHERE league = %s 
      AND home_team = %s 
      AND away_team = %s
      AND timestamp >= NOW() - INTERVAL '24 hours'
    ORDER BY timestamp ASC
    """
    
    cursor.execute(query, (league, home_team, away_team))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows or len(rows) < 1:
        return None
    
    # First snapshot (open)
    open_row = rows[0]
    open_home = float(open_row[0])
    open_draw = float(open_row[1])
    open_away = float(open_row[2])
    open_timestamp = open_row[3]
    
    # Latest snapshot (current)
    current_row = rows[-1]
    current_home = float(current_row[0])
    current_draw = float(current_row[1])
    current_away = float(current_row[2])
    current_timestamp = current_row[3]
    
    # Calculate no-vig probabilities
    open_probs = calculate_no_vig_probabilities(open_home, open_draw, open_away)
    current_probs = calculate_no_vig_probabilities(current_home, current_draw, current_away)
    
    # Calculate absolute changes in probability
    # Note: When odds go DOWN, probability goes UP (inverse relationship)
    # So we need to track odds direction, not probability direction
    odds_changes = [
        (current_home - open_home, 'Home', current_home, open_home),
        (current_draw - open_draw, 'Draw', current_draw, open_draw),
        (current_away - open_away, 'Away', current_away, open_away)
    ]
    
    # Calculate probability changes
    # Formula: p_now_nv - p_open_nv (probability delta)
    # When odds increase, probability decreases → delta is negative → show negative
    # When odds decrease, probability increases → delta is positive → show positive
    prob_changes = [
        (abs(current_probs[0] - open_probs[0]) / open_probs[0] * 100, 'Home', current_probs[0] - open_probs[0]),
        (abs(current_probs[1] - open_probs[1]) / open_probs[1] * 100, 'Draw', current_probs[1] - open_probs[1]),
        (abs(current_probs[2] - open_probs[2]) / open_probs[2] * 100, 'Away', current_probs[2] - open_probs[2])
    ]
    
    # Find biggest absolute probability change
    biggest_prob_change = max(prob_changes, key=lambda x: x[0])
    change_percent = biggest_prob_change[0]
    change_label = biggest_prob_change[1]
    prob_delta = biggest_prob_change[2]  # This is p_now_nv - p_open_nv
    
    # Determine direction based on PROBABILITY delta (not odds direction)
    # If probability delta is positive (probability increased, odds decreased), show positive
    # If probability delta is negative (probability decreased, odds increased), show negative
    change_direction = '+' if prob_delta > 0 else '-'
    
    # Calculate minutes ago
    minutes_ago = int((datetime.now() - current_timestamp).total_seconds() / 60)
    
    return {
        'open_home': open_home,
        'open_draw': open_draw,
        'open_away': open_away,
        'current_home': current_home,
        'current_draw': current_draw,
        'current_away': current_away,
        'move_label': change_label,
        'move_percent': change_percent,
        'move_direction': change_direction,
        'minutes_ago': minutes_ago
    }

# Sidebar filters
st.sidebar.header("Filters")

# Load current odds
odds_data = load_latest_odds()

if not odds_data:
    st.warning("No odds data available yet. The data collector may still be gathering initial data.")
    st.info("Check back in a few minutes, or verify that the data collector is running.")
else:
    # Extract unique values for filters
    all_leagues = sorted(set(row[0] for row in odds_data))
    all_bookmakers = sorted(set(row[3] for row in odds_data))
    
    # League filter
    leagues = ['All'] + all_leagues
    selected_league = st.sidebar.selectbox("League", leagues)
    
    # Bookmaker filter
    bookmakers = ['All'] + all_bookmakers
    selected_bookmaker = st.sidebar.selectbox("Bookmaker", bookmakers)
    
    # Date filter (showing next 2-3 days only)
    date_options = ['All', 'Today', 'Tomorrow']
    selected_date = st.sidebar.selectbox("Date", date_options)
    
    # Apply filters
    filtered_data = odds_data
    if selected_league != 'All':
        filtered_data = [row for row in filtered_data if row[0] == selected_league]
    if selected_bookmaker != 'All':
        filtered_data = [row for row in filtered_data if row[3] == selected_bookmaker]
    if selected_date == 'Today':
        today = datetime.now().date()
        # Use commence_time if available, else timestamp
        filtered_data = [row for row in filtered_data if (row[8].date() if row[8] else row[7].date()) == today]
    elif selected_date == 'Tomorrow':
        tomorrow = (datetime.now().date() + timedelta(days=1))
        # Use commence_time if available
        filtered_data = [row for row in filtered_data if row[8] and row[8].date() == tomorrow]
    
    # Calculate feed freshness (latest update time)
    if filtered_data:
        latest_update = max(row[7] for row in filtered_data)
        minutes_ago = int((datetime.now() - latest_update).total_seconds() / 60)
        # Add freshness indicator to sidebar
        st.sidebar.markdown("---")
        st.sidebar.caption(f"Feed active · updated {minutes_ago}m ago")
    
    # Group by date first, then by match
    # First pass: collect all rows for each match and determine the best date
    match_rows = {}
    for row in filtered_data:
        league, home, away = row[0], row[1], row[2]
        key = (league, home, away)
        
        if key not in match_rows:
            match_rows[key] = []
        match_rows[key].append(row)
    
    # Determine the date for each match (prefer commence_time from any row)
    match_dates = {}
    for key, rows in match_rows.items():
        # Look for any row with commence_time - that's the match date
        match_date = None
        for row in rows:
            if row[8]:  # commence_time exists
                match_date = row[8].date()
                break
        
        # If no commence_time found, use timestamp from first row
        if match_date is None:
            match_date = rows[0][7].date()
        
        match_dates[key] = match_date
    
    # Now group matches by their correct dates
    matches_by_date = {}
    for key, rows in match_rows.items():
        match_date = match_dates[key]
        
        if match_date not in matches_by_date:
            matches_by_date[match_date] = {}
        
        matches_by_date[match_date][key] = rows
    
    # Display matches grouped by date (today first, then future dates)
    for match_date in sorted(matches_by_date.keys()):
        # Check if date is today
        if match_date == datetime.now().date():
            st.subheader(f"📅 Today - {match_date.strftime('%A, %B %d, %Y')}")
        else:
            st.subheader(f"📅 {match_date.strftime('%A, %B %d, %Y')}")
        
        for (league, home, away), match_data in matches_by_date[match_date].items():
            # Check if match is live (commence_time has passed but not too long ago)
            is_live = False
            commence_time = None
            for row in match_data:
                if row[8]:  # commence_time exists
                    commence_time = row[8]
                    # Handle timezone-aware datetime
                    if commence_time.tzinfo:
                        now = datetime.now(commence_time.tzinfo)
                    else:
                        now = datetime.now()
                    # Match is live if it started and is within 3 hours (typical match duration + overtime)
                    time_since_start = (now - commence_time).total_seconds() / 3600
                    if commence_time <= now and time_since_start < 3:
                        is_live = True
                    break
            
            # Skip matches that have started more than 3 hours ago
            if commence_time:
                if commence_time.tzinfo:
                    now = datetime.now(commence_time.tzinfo)
                else:
                    now = datetime.now()
                if (now - commence_time).total_seconds() / 3600 > 3:
                    continue  # Skip this match, it's finished
            
            # Get movement summary for collapsed row display
            summary = get_match_movement_summary(league, home, away)
            
            # Display match title with summary (always visible)
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown(f"**⚽ {home} vs {away} ({league})**")
            with col2:
                # Display LIVE indicator on the right side if match is live
                if is_live:
                    st.markdown('<div class="live-indicator">🔴 LIVE</div>', unsafe_allow_html=True)
                
                if summary:
                    # Determine color for move (green for +, red for -)
                    move_color = "green" if summary['move_direction'] == '+' else "red"
                    move_sign = summary['move_direction'] if summary['move_direction'] == '-' else '+'  # Show - for negative, + for positive
                    
                    # Format summary as two-line layout
                    # Line 1: Move and Updated (primary, larger)
                    line1 = (
                        f"<div class='move-summary-line1'>"
                        f"<strong>Move:</strong> {summary['move_label']} "
                        f"<span style='color: {move_color}; font-weight: 600;'>{move_sign}{summary['move_percent']:.2f}%</span> "
                        f"· Updated {summary['minutes_ago']}m ago"
                        f"</div>"
                    )
                    # Line 2: Odds comparison (secondary, smaller, muted)
                    line2 = (
                        f"<div class='move-summary-line2'>"
                        f"Open: {summary['open_home']:.2f} / {summary['open_draw']:.2f} / {summary['open_away']:.2f} → "
                        f"Now: {summary['current_home']:.2f} / {summary['current_draw']:.2f} / {summary['current_away']:.2f}"
                        f"</div>"
                    )
                    st.markdown(line1 + line2, unsafe_allow_html=True)
            
            with st.expander("View details", expanded=False):
                
                # Display odds table
                st.subheader("Current Odds")
                
                # Create table
                table_data = []
                for row in match_data:
                    bookmaker = row[3]
                    home_odds = row[4]
                    draw_odds = row[6]
                    away_odds = row[5]
                    timestamp = row[7].strftime('%H:%M:%S')
                    table_data.append({
                        'Bookmaker': bookmaker,
                        'Home': f"{home_odds:.2f}",
                        'Draw': f"{draw_odds:.2f}",
                        'Away': f"{away_odds:.2f}",
                        'Updated': timestamp
                    })
                
                # Display as dataframe
                st.dataframe(table_data, use_container_width=True, hide_index=True)
                
                # Historical trends
                st.subheader("Odds Movement (Last 24h)")
                
                history_data = load_odds_history(league, home, away, hours=24)
                
                if history_data and len(history_data) >= 2:
                    # Since we only track Pinnacle, get all data and sort by timestamp
                    history = []
                    for row in history_data:
                        history.append({
                            'timestamp': row[4],
                            'home_odds': row[1],
                            'draw_odds': row[3],
                            'away_odds': row[2]
                        })
                    
                    # Sort by timestamp to ensure chronological order
                    history.sort(key=lambda x: x['timestamp'])
                    
                    # Remove duplicates - keep only latest entry for each timestamp
                    seen_timestamps = set()
                    unique_history = []
                    for h in reversed(history):  # Start from newest
                        if h['timestamp'] not in seen_timestamps:
                            seen_timestamps.add(h['timestamp'])
                            unique_history.append(h)
                    unique_history.reverse()  # Back to chronological order
                    
                    if len(unique_history) >= 2:
                        # Create dataframe with proper datetime index
                        timestamps = [h['timestamp'] for h in unique_history]
                        home_vals = [float(h['home_odds']) for h in unique_history]
                        draw_vals = [float(h['draw_odds']) for h in unique_history]
                        away_vals = [float(h['away_odds']) for h in unique_history]
                            
                        # Calculate Y-axis range based on actual data with padding
                        all_vals = home_vals + draw_vals + away_vals
                        if all_vals:
                            y_min = min(all_vals)
                            y_max = max(all_vals)
                            # Add 10% padding above and below for better visualization
                            padding = (y_max - y_min) * 0.1
                            y_range = [max(0, y_min - padding), y_max + padding]
                        else:
                            y_range = None
                        
                        # Create Plotly figure with custom Y-axis range
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=home_vals,
                            mode='lines+markers',
                            name='Home',
                            line=dict(color='#FF6B6B', width=2)
                        ))
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=draw_vals,
                            mode='lines+markers',
                            name='Draw',
                            line=dict(color='#4ECDC4', width=2)
                        ))
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=away_vals,
                            mode='lines+markers',
                            name='Away',
                            line=dict(color='#95E1D3', width=2)
                        ))
                        
                        # Update layout with custom Y-axis range
                        fig.update_layout(
                            height=400,
                            xaxis_title="Time",
                            yaxis_title="Odds",
                            yaxis=dict(range=y_range) if y_range else {},
                            hovermode='x unified',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white')
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                            
                else:
                    st.info("Not enough historical data yet. Check back after a few updates.")
    
    # Auto-refresh toggle
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Page will refresh every 60 seconds")
        import time
        time.sleep(60)
        st.rerun()

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking | Data updates every 15 minutes")