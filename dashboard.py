import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os
import pandas as pd

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
    
    # Calculate metrics
    unique_matches = set((row[0], row[1], row[2]) for row in filtered_data)
    unique_leagues = set(row[0] for row in filtered_data)
    unique_bookmakers = set(row[3] for row in filtered_data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", len(unique_matches))
    with col2:
        st.metric("Leagues", len(unique_leagues))
    with col3:
        st.metric("Bookmakers", len(unique_bookmakers))
    with col4:
        if filtered_data:
            latest_update = max(row[7] for row in filtered_data)
            minutes_ago = int((datetime.now() - latest_update).total_seconds() / 60)
            st.metric("Last Update", f"{minutes_ago}m ago")
    
    st.markdown("---")
    
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
    
    # Display matches grouped by date
    for match_date in sorted(matches_by_date.keys(), reverse=True):
        # Check if date is today
        if match_date == datetime.now().date():
            st.subheader(f"📅 Today - {match_date.strftime('%A, %B %d, %Y')}")
        else:
            st.subheader(f"📅 {match_date.strftime('%A, %B %d, %Y')}")
        
        for (league, home, away), match_data in matches_by_date[match_date].items():
            with st.expander(f"⚽ {home} vs {away} ({league})", expanded=False):
                
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
                    # Group by bookmaker
                    bookmaker_history = {}
                    for row in history_data:
                        bookmaker = row[0]
                        if bookmaker not in bookmaker_history:
                            bookmaker_history[bookmaker] = []
                        bookmaker_history[bookmaker].append({
                            'timestamp': row[4],
                            'home_odds': row[1],
                            'draw_odds': row[3],
                            'away_odds': row[2]
                        })
                    
                    # Display charts for each bookmaker
                    for bookmaker, history in bookmaker_history.items():
                        if len(history) >= 2:
                            st.write(f"**{bookmaker}**")
                            
                            # Create dataframe with proper datetime index
                            timestamps = [h['timestamp'] for h in history]
                            home_vals = [float(h['home_odds']) for h in history]
                            draw_vals = [float(h['draw_odds']) for h in history]
                            away_vals = [float(h['away_odds']) for h in history]
                            
                            df = pd.DataFrame({
                                'Home': home_vals,
                                'Draw': draw_vals,
                                'Away': away_vals
                            }, index=timestamps)
                            
                            st.line_chart(df)
                            
                            # Best odds with movement indicators
                            st.subheader("Best Odds")
                            col1, col2, col3 = st.columns(3)
                            
                            # Calculate directions
                            home_arrow, home_color = get_odds_direction(history, 'home_odds')
                            draw_arrow, draw_color = get_odds_direction(history, 'draw_odds')
                            away_arrow, away_color = get_odds_direction(history, 'away_odds')
                            
                            # Current odds (latest)
                            current_home = history[-1]['home_odds']
                            current_draw = history[-1]['draw_odds']
                            current_away = history[-1]['away_odds']
                            
                            with col1:
                                if home_arrow:
                                    st.metric(
                                        f"Home ({home})",
                                        f"{current_home:.2f}",
                                        f"{home_arrow} {bookmaker}",
                                        delta_color="normal" if home_color == "green" else "inverse"
                                    )
                                else:
                                    st.metric(f"Home ({home})", f"{current_home:.2f}", f"{bookmaker}")
                            
                            with col2:
                                if draw_arrow:
                                    st.metric(
                                        "Draw",
                                        f"{current_draw:.2f}",
                                        f"{draw_arrow} {bookmaker}",
                                        delta_color="normal" if draw_color == "green" else "inverse"
                                    )
                                else:
                                    st.metric("Draw", f"{current_draw:.2f}", f"{bookmaker}")
                            
                            with col3:
                                if away_arrow:
                                    st.metric(
                                        f"Away ({away})",
                                        f"{current_away:.2f}",
                                        f"{away_arrow} {bookmaker}",
                                        delta_color="normal" if away_color == "green" else "inverse"
                                    )
                                else:
                                    st.metric(f"Away ({away})", f"{current_away:.2f}", f"{bookmaker}")
                            
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