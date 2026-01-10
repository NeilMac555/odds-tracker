import streamlit as st
import sqlite3
import pandas as pd
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
DB_PATH = "odds_tracker.db"

def get_db_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def load_latest_odds():
    """Load the most recent odds for each match"""
    conn = get_db_connection()
    
    query = """
    WITH RankedOdds AS (
        SELECT 
            league,
            home_team,
            away_team,
            bookmaker,
            home_odds,
            away_odds,
            draw_odds,
            timestamp,
            ROW_NUMBER() OVER (
                PARTITION BY league, home_team, away_team, bookmaker 
                ORDER BY timestamp DESC
            ) as rn
        FROM odds
        WHERE timestamp >= datetime('now', '-24 hours')
    )
    SELECT 
        league,
        home_team,
        away_team,
        bookmaker,
        home_odds,
        away_odds,
        draw_odds,
        timestamp
    FROM RankedOdds
    WHERE rn = 1
    ORDER BY league, home_team, bookmaker
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def load_odds_history(league, home_team, away_team, hours=24):
    """Load historical odds for a specific match"""
    conn = get_db_connection()
    
    query = """
    SELECT 
        bookmaker,
        home_odds,
        away_odds,
        draw_odds,
        timestamp
    FROM odds
    WHERE league = ? 
        AND home_team = ? 
        AND away_team = ?
        AND timestamp >= datetime('now', ? || ' hours')
    ORDER BY timestamp ASC
    """
    
    df = pd.read_sql_query(query, conn, params=(league, home_team, away_team, f'-{hours}'))
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Load current odds
df = load_latest_odds()

if df.empty:
    st.warning("No odds data available yet. The data collector may still be gathering initial data.")
    st.info("Check back in a few minutes, or verify that the data collector is running.")
else:
    # League filter
    leagues = ['All'] + sorted(df['league'].unique().tolist())
    selected_league = st.sidebar.selectbox("League", leagues)
    
    # Bookmaker filter
    bookmakers = ['All'] + sorted(df['bookmaker'].unique().tolist())
    selected_bookmaker = st.sidebar.selectbox("Bookmaker", bookmakers)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_league != 'All':
        filtered_df = filtered_df[filtered_df['league'] == selected_league]
    if selected_bookmaker != 'All':
        filtered_df = filtered_df[filtered_df['bookmaker'] == selected_bookmaker]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", len(filtered_df.groupby(['home_team', 'away_team'])))
    with col2:
        st.metric("Leagues", filtered_df['league'].nunique())
    with col3:
        st.metric("Bookmakers", filtered_df['bookmaker'].nunique())
    with col4:
        if not filtered_df.empty:
            latest_update = filtered_df['timestamp'].max()
            minutes_ago = int((datetime.now() - latest_update).total_seconds() / 60)
            st.metric("Last Update", f"{minutes_ago}m ago")
    
    st.markdown("---")
    
    # Group by match and display
    matches = filtered_df.groupby(['league', 'home_team', 'away_team'])
    
    for (league, home, away), match_df in matches:
        with st.expander(f"⚽ {home} vs {away} ({league})", expanded=False):
            
            # Display odds table
            st.subheader("Current Odds")
            
            odds_display = match_df[['bookmaker', 'home_odds', 'draw_odds', 'away_odds', 'timestamp']].copy()
            odds_display['timestamp'] = odds_display['timestamp'].dt.strftime('%H:%M:%S')
            odds_display.columns = ['Bookmaker', 'Home', 'Draw', 'Away', 'Updated']
            
            st.dataframe(
                odds_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Best odds highlighting
            st.subheader("Best Odds")
            col1, col2, col3 = st.columns(3)
            
            best_home = match_df.loc[match_df['home_odds'].idxmax()]
            best_draw = match_df.loc[match_df['draw_odds'].idxmax()]
            best_away = match_df.loc[match_df['away_odds'].idxmax()]
            
            with col1:
                st.metric(
                    f"Home ({home})",
                    f"{best_home['home_odds']:.2f}",
                    f"{best_home['bookmaker']}"
                )
            with col2:
                st.metric(
                    "Draw",
                    f"{best_draw['draw_odds']:.2f}",
                    f"{best_draw['bookmaker']}"
                )
            with col3:
                st.metric(
                    f"Away ({away})",
                    f"{best_away['away_odds']:.2f}",
                    f"{best_away['bookmaker']}"
                )
            
            # Historical trends
            st.subheader("Odds Movement (Last 24h)")
            
            history_df = load_odds_history(league, home, away, hours=24)
            
            if not history_df.empty:
                # Pivot data for plotting
                for bookmaker in history_df['bookmaker'].unique():
                    bookie_data = history_df[history_df['bookmaker'] == bookmaker].copy()
                    bookie_data = bookie_data.set_index('timestamp')
                    
                    st.write(f"**{bookmaker}**")
                    st.line_chart(bookie_data[['home_odds', 'draw_odds', 'away_odds']])
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
st.caption("OddsEdge - Professional Odds Tracking | Data updates every 5 minutes")
