import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.graph_objects as go

# Page configuration with custom favicon
st.set_page_config(
    page_title="OddsEdge - Live Odds Tracker",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding and segmented control
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
    
    /* Segmented Control Styling - ONLY for Home/Draw/Away tabs inside expanders */
    /* Completely exclude sidebar - use very specific selectors */
    section[data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stRadio,
    .css-1d391kg .stRadio {
        all: unset !important;
        display: block !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div,
    [data-testid="stSidebar"] .stRadio > div,
    .css-1d391kg .stRadio > div {
        all: revert !important;
    }
    
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label,
    .css-1d391kg .stRadio label {
        all: revert !important;
    }
    
    /* Target ONLY radio buttons inside expander content (where Home/Draw/Away tabs are) */
    .stExpander .element-container .stRadio > div {
        display: flex !important;
        gap: 6px !important;
        margin-bottom: 12px !important;
        flex-direction: row !important;
    }
    
    .stExpander .element-container .stRadio > div[role="radiogroup"] {
        display: flex !important;
        gap: 6px !important;
        width: 100% !important;
        flex-direction: row !important;
    }
    
    /* Compact tab styling - only in expanders */
    .stExpander .element-container .stRadio > div > label,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label {
        flex: 1 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: rgba(255, 255, 255, 0.6) !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        position: relative !important;
        margin-bottom: 0 !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 32px !important;
        box-sizing: border-box !important;
        font-size: 0.9rem !important;
    }
    
    .stExpander .element-container .stRadio > div > label:hover,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Active tab styling - only in expanders */
    .stExpander .element-container .stRadio > div > label:has(input[type="radio"]:checked),
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        font-weight: 600 !important;
    }
    
    /* Active tab underline - only in expanders */
    .stExpander .element-container .stRadio > div > label:has(input[type="radio"]:checked)::after,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:has(input[type="radio"]:checked)::after {
        content: '' !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 2px !important;
        background-color: #4ECDC4 !important;
        border-radius: 0 0 6px 6px !important;
    }
    
    /* Hide default radio button circles - only in expanders */
    .stExpander .element-container .stRadio input[type="radio"] {
        position: absolute !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        pointer-events: none !important;
    }
    
    /* Ensure proper spacing - only in expanders */
    .stExpander .element-container .stRadio {
        margin-bottom: 8px !important;
    }
    
    /* Style the label text container - only in expanders */
    .stExpander .element-container .stRadio label > div {
        width: 100% !important;
        text-align: center !important;
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
    """Load the most recent odds for each match (next 3 days only)"""
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

def get_opening_odds(league, home_team, away_team, bookmaker):
    """Get the first recorded odds for a match (opening odds)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT home_odds, away_odds, draw_odds, timestamp
    FROM odds
    WHERE league = %s 
        AND home_team = %s 
        AND away_team = %s
        AND bookmaker = %s
    ORDER BY timestamp ASC
    LIMIT 1
    """
    
    cursor.execute(query, (league, home_team, away_team, bookmaker))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'home_odds': row[0],
            'away_odds': row[1],
            'draw_odds': row[2],
            'timestamp': row[3]
        }
    return None

def calculate_odds_change(opening_odds, current_odds):
    """Calculate percentage change and direction for odds"""
    if opening_odds is None or current_odds is None:
        return None, None, None
    
    change = ((current_odds - opening_odds) / opening_odds) * 100
    
    if change > 0:
        # Odds increased (less likely to win) - green up arrow
        return change, "↑", "green"
    elif change < 0:
        # Odds decreased (more likely to win) - red down arrow
        return abs(change), "↓", "red"
    else:
        # No change
        return 0, "—", "gray"

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

# League to flag emoji mapping
LEAGUE_FLAGS = {
    'EPL': '🇬🇧',
    'Italy Serie A': '🇮🇹',
    'Spain La Liga': '🇪🇸',
    'Germany Bundesliga': '🇩🇪',
    'France Ligue One': '🇫🇷'
}

# League navigation mapping (database name -> display name with flag)
LEAGUE_DISPLAY_NAMES = {
    None: '🌍 All Leagues',
    'EPL': f"{LEAGUE_FLAGS.get('EPL', '')} Premier League",
    'Italy Serie A': f"{LEAGUE_FLAGS.get('Italy Serie A', '')} Serie A",
    'Spain La Liga': f"{LEAGUE_FLAGS.get('Spain La Liga', '')} La Liga",
    'Germany Bundesliga': f"{LEAGUE_FLAGS.get('Germany Bundesliga', '')} Bundesliga",
    'France Ligue One': f"{LEAGUE_FLAGS.get('France Ligue One', '')} Ligue 1"
}

def get_league_flag(league):
    """Get the flag emoji for a league"""
    return LEAGUE_FLAGS.get(league, '⚽')

# Supported leagues (always show all, even if 0 matches)
SUPPORTED_LEAGUES = ['EPL', 'Italy Serie A', 'Spain La Liga', 'Germany Bundesliga', 'France Ligue One']

# Load current odds
odds_data = load_latest_odds()

# League navigation in sidebar
st.sidebar.markdown("### Leagues")

# Create league options for radio button
league_options = [LEAGUE_DISPLAY_NAMES[None]] + [LEAGUE_DISPLAY_NAMES[league] for league in SUPPORTED_LEAGUES]
league_values = [None] + SUPPORTED_LEAGUES

# Use radio button for league selection
selected_league_display = st.sidebar.radio(
    "Select League",
    options=league_options,
    index=0,
    label_visibility="collapsed"
)

# Map display name back to database name
selected_league = None if selected_league_display == LEAGUE_DISPLAY_NAMES[None] else league_values[league_options.index(selected_league_display)]

if not odds_data:
    st.warning("No odds data available yet. The data collector may still be gathering initial data.")
    st.info("Check back in a few minutes, or verify that the data collector is running.")
else:
    # Apply league filter
    filtered_data = odds_data
    if selected_league is not None:
        filtered_data = [row for row in filtered_data if row[0] == selected_league]
    
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
    matches_by_date = {}
    for row in filtered_data:
        league, home, away = row[0], row[1], row[2]
        match_date = row[8].date() if row[8] else row[7].date()  # Use commence_time if available, else timestamp
        
        if match_date not in matches_by_date:
            matches_by_date[match_date] = {}
        
        key = (league, home, away)
        if key not in matches_by_date[match_date]:
            matches_by_date[match_date][key] = []
        matches_by_date[match_date][key].append(row)
    
    # Display matches grouped by date (earliest first - today at top)
    for match_date in sorted(matches_by_date.keys()):
        # Check if date is today
        if match_date == datetime.now().date():
            st.subheader(f"📅 Today - {match_date.strftime('%A, %B %d, %Y')}")
        else:
            st.subheader(f"📅 {match_date.strftime('%A, %B %d, %Y')}")
        
        for (league, home, away), match_data in matches_by_date[match_date].items():
            league_flag = get_league_flag(league)
            with st.expander(f"{league_flag} {home} vs {away} ({league})", expanded=False):
                
                # Display odds table
                st.subheader("Current Odds")
                
                # Get opening odds for comparison
                league, home, away = match_data[0][0], match_data[0][1], match_data[0][2]
                
                # Create table with opening odds comparison
                table_rows = []
                for row in match_data:
                    bookmaker = row[3]
                    home_odds = row[4]
                    draw_odds = row[6]
                    away_odds = row[5]
                    timestamp = row[7].strftime('%H:%M:%S')
                    
                    # Get opening odds for this bookmaker
                    opening = get_opening_odds(league, home, away, bookmaker)
                    
                    # Format Home odds with change indicator
                    if opening:
                        home_change, home_arrow, home_color = calculate_odds_change(opening['home_odds'], home_odds)
                        if home_change is not None and home_change > 0:
                            arrow_color = "#00ff00" if home_color == "green" else "#ff0000"
                            home_display = f"{opening['home_odds']:.2f} → {home_odds:.2f} <span style='color: {arrow_color}; font-weight: bold;'>{home_arrow} {home_change:.1f}%</span>"
                        else:
                            home_display = f"{opening['home_odds']:.2f} → {home_odds:.2f} (— 0.0%)"
                    else:
                        home_display = f"{home_odds:.2f} (No opening data)"
                    
                    # Format Draw odds with change indicator
                    if opening:
                        draw_change, draw_arrow, draw_color = calculate_odds_change(opening['draw_odds'], draw_odds)
                        if draw_change is not None and draw_change > 0:
                            arrow_color = "#00ff00" if draw_color == "green" else "#ff0000"
                            draw_display = f"{opening['draw_odds']:.2f} → {draw_odds:.2f} <span style='color: {arrow_color}; font-weight: bold;'>{draw_arrow} {draw_change:.1f}%</span>"
                        else:
                            draw_display = f"{opening['draw_odds']:.2f} → {draw_odds:.2f} (— 0.0%)"
                    else:
                        draw_display = f"{draw_odds:.2f} (No opening data)"
                    
                    # Format Away odds with change indicator
                    if opening:
                        away_change, away_arrow, away_color = calculate_odds_change(opening['away_odds'], away_odds)
                        if away_change is not None and away_change > 0:
                            arrow_color = "#00ff00" if away_color == "green" else "#ff0000"
                            away_display = f"{opening['away_odds']:.2f} → {away_odds:.2f} <span style='color: {arrow_color}; font-weight: bold;'>{away_arrow} {away_change:.1f}%</span>"
                        else:
                            away_display = f"{opening['away_odds']:.2f} → {away_odds:.2f} (— 0.0%)"
                    else:
                        away_display = f"{away_odds:.2f} (No opening data)"
                    
                    table_rows.append({
                        'Bookmaker': bookmaker,
                        'Home': home_display,
                        'Draw': draw_display,
                        'Away': away_display,
                        'Updated': timestamp
                    })
                
                # Create HTML table for better formatting
                html_table = "<table style='width: 100%; border-collapse: collapse;'>"
                html_table += "<thead><tr style='border-bottom: 2px solid rgba(255,255,255,0.2);'>"
                html_table += "<th style='text-align: left; padding: 8px;'>Bookmaker</th>"
                html_table += "<th style='text-align: center; padding: 8px;'>Home</th>"
                html_table += "<th style='text-align: center; padding: 8px;'>Draw</th>"
                html_table += "<th style='text-align: center; padding: 8px;'>Away</th>"
                html_table += "<th style='text-align: right; padding: 8px;'>Updated</th>"
                html_table += "</tr></thead><tbody>"
                
                for row_data in table_rows:
                    html_table += "<tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>"
                    html_table += f"<td style='padding: 8px;'><strong>{row_data['Bookmaker']}</strong></td>"
                    html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Home']}</td>"
                    html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Draw']}</td>"
                    html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Away']}</td>"
                    html_table += f"<td style='padding: 8px; text-align: right;'>{row_data['Updated']}</td>"
                    html_table += "</tr>"
                
                html_table += "</tbody></table>"
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Historical trends
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
                        
                        # Get opening and current values for each outcome
                        home_open = home_vals[0]
                        home_now = home_vals[-1]
                        draw_open = draw_vals[0]
                        draw_now = draw_vals[-1]
                        away_open = away_vals[0]
                        away_now = away_vals[-1]
                        
                        # Create unique key for this match's tab state
                        match_key = f"{league}_{home}_{away}_tab"
                        
                        # Segmented control tabs (placed before subheader)
                        selected_tab = st.radio(
                            "Outcome",
                            ["Home", "Draw", "Away"],
                            key=match_key,
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        
                        # Chart title
                        st.subheader("Odds Movement (Last 24h)")
                        
                        # Helper function to create a focused graph for a single outcome
                        def create_focused_graph(timestamps, values, outcome_name, color, open_val, now_val):
                            # Calculate Y-axis range based on this outcome's data with padding
                            if values:
                                y_min = min(values)
                                y_max = max(values)
                                # Add 5% padding above and below for better visualization
                                padding = (y_max - y_min) * 0.05
                                if padding == 0:  # If all values are the same, add small fixed padding
                                    padding = y_min * 0.01 if y_min > 0 else 0.1
                                y_range = [max(0, y_min - padding), y_max + padding]
                            else:
                                y_range = None
                            
                            # Create Plotly figure with focused Y-axis range
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=timestamps,
                                y=values,
                                mode='lines+markers',
                                name=outcome_name,
                                line=dict(color=color, width=2),
                                marker=dict(size=4)
                            ))
                            
                            # Update layout with custom Y-axis range
                            fig.update_layout(
                                height=400,
                                xaxis_title="Time",
                                yaxis_title="Odds",
                                yaxis=dict(range=y_range) if y_range else {},
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white')
                            )
                            
                            return fig
                        
                        # Display content based on selected tab
                        if selected_tab == "Home":
                            st.markdown(f"**Open:** {home_open:.2f} • **Now:** {home_now:.2f}")
                            fig_home = create_focused_graph(timestamps, home_vals, 'Home', '#FF6B6B', home_open, home_now)
                            st.plotly_chart(fig_home, use_container_width=True)
                        elif selected_tab == "Draw":
                            st.markdown(f"**Open:** {draw_open:.2f} • **Now:** {draw_now:.2f}")
                            fig_draw = create_focused_graph(timestamps, draw_vals, 'Draw', '#4ECDC4', draw_open, draw_now)
                            st.plotly_chart(fig_draw, use_container_width=True)
                        else:  # Away
                            st.markdown(f"**Open:** {away_open:.2f} • **Now:** {away_now:.2f}")
                            fig_away = create_focused_graph(timestamps, away_vals, 'Away', '#95E1D3', away_open, away_now)
                            st.plotly_chart(fig_away, use_container_width=True)
                            
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