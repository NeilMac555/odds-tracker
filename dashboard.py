import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os

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
    SELECT league, home_team, away_team, bookmaker, home_odds, away_odds, draw_odds, timestamp
    FROM (
        SELECT *, 
               ROW_NUMBER() OVER (
                   PARTITION BY league, home_team, away_team, bookmaker 
                   ORDER BY timestamp DESC
               ) as rn
        FROM odds
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
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
    
    # Apply filters
    filtered_data = odds_data
    if selected_league != 'All':
        filtered_data = [row for row in filtered_data if row[0] == selected_league]
    if selected_bookmaker != 'All':
        filtered_data = [row for row in filtered_data if row[3] == selected_bookmaker]
    
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
    
    # Group by match
    matches = {}
    for row in filtered_data:
        league, home, away = row[0], row[1], row[2]
        key = (league, home, away)
        if key not in matches:
            matches[key] = []
        matches[key].append(row)
    
    # Display each match
    for (league, home, away), match_data in matches.items():
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
            
            # Best odds highlighting
            st.subheader("Best Odds")
            col1, col2, col3 = st.columns(3)
            
            # Find best odds
            best_home = max(match_data, key=lambda x: x[4])
            best_draw = max(match_data, key=lambda x: x[6])
            best_away = max(match_data, key=lambda x: x[5])
            
            with col1:
                st.metric(
                    f"Home ({home})",
                    f"{best_home[4]:.2f}",
                    f"{best_home[3]}"
                )
            with col2:
                st.metric(
                    "Draw",
                    f"{best_draw[6]:.2f}",
                    f"{best_draw[3]}"
                )
            with col3:
                st.metric(
                    f"Away ({away})",
                    f"{best_away[5]:.2f}",
                    f"{best_away[3]}"
                )
            
            # Historical trends
            st.subheader("Odds Movement (Last 24h)")
            
            history_data = load_odds_history(league, home, away, hours=24)
            
            if history_data:
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
                    st.write(f"**{bookmaker}**")
                    
                    # Create chart data as lists
                    chart_data = {
                        'Home': [],
                        'Draw': [],
                        'Away': []
                    }
                    
                    for h in history:
                        chart_data['Home'].append(float(h['home_odds']))
                        chart_data['Draw'].append(float(h['draw_odds']))
                        chart_data['Away'].append(float(h['away_odds']))
                    
                    # Only show chart if we have data
                    if chart_data['Home']:
                        st.line_chart(chart_dat