import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="Biggest Movers - OddsEdge",
    page_icon="📊",
    layout="wide"
)

# Custom CSS with modern typography and spacing
st.markdown("""
    <style>
    /* Modern typography system */
    .stApp {
        font-size: 16px;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1.5rem;
        font-weight: 400;
        letter-spacing: -0.01em;
    }
    
    /* Modern card styling - compact rows */
    .mover-card {
        padding: 10px 18px;
        margin-bottom: 6px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(0, 0, 0, 0.25);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .mover-card:hover {
        background-color: rgba(0, 0, 0, 0.35);
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.18), 0 1px 4px rgba(0, 0, 0, 0.12);
        transform: translateY(-1px);
    }
    
    .mover-match {
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 3px;
        letter-spacing: -0.01em;
        line-height: 1.35;
    }
    
    .mover-details {
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.9rem;
        margin-top: 2px;
        display: inline-block;
        line-height: 1.4;
    }
    
    .mover-line-primary {
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .mover-line-secondary {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.4;
    }
    
    .strength-badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 6px;
        vertical-align: middle;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .strength-badge.strong {
        background-color: rgba(255, 100, 100, 0.2);
        color: #ff6464;
        border: 1px solid rgba(255, 100, 100, 0.3);
    }
    
    .strength-badge.medium {
        background-color: rgba(255, 200, 100, 0.2);
        color: #ffc864;
        border: 1px solid rgba(255, 200, 100, 0.3);
    }
    
    /* Subtle animated arrow indicators */
    @keyframes gentleMoveUp {
        0%, 100% {
            transform: translateY(0);
            opacity: 0.6;
        }
        50% {
            transform: translateY(-3px);
            opacity: 0.8;
        }
    }
    
    @keyframes gentleMoveDown {
        0%, 100% {
            transform: translateY(0);
            opacity: 0.6;
        }
        50% {
            transform: translateY(3px);
            opacity: 0.8;
        }
    }
    
    .arrow-shortening {
        display: inline-block;
        animation: gentleMoveUp 2.5s ease-in-out infinite;
        opacity: 0.65;
    }
    
    .arrow-drifting {
        display: inline-block;
        animation: gentleMoveDown 2.5s ease-in-out infinite;
        opacity: 0.65;
    }
    
    /* Live indicator - subtle pulsing dot */
    @keyframes subtlePulse {
        0%, 100% {
            opacity: 0.6;
            transform: scale(1);
        }
        50% {
            opacity: 1;
            transform: scale(1.1);
        }
    }
    
    .live-indicator {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-left: 6px;
        vertical-align: middle;
        animation: subtlePulse 2s ease-in-out infinite;
        box-shadow: 0 0 4px currentColor;
    }
    
    .live-indicator.live-shortening {
        background-color: #44ff44;
        color: #44ff44;
    }
    
    .live-indicator.live-drifting {
        background-color: #ff4444;
        color: #ff4444;
    }
    
    /* Remove heavy dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 2rem 0;
    }
    
    /* Increase spacing between sections */
    .element-container {
        margin-bottom: 2rem;
    }
    
    /* Constrain main content column width and center it */
    .main .block-container {
        max-width: 950px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Header Section
st.markdown('<p class="main-header">📊 Biggest Movers</p>', unsafe_allow_html=True)

# Use shared time window selector from dashboard (session state)
if 'time_window_selection' not in st.session_state:
    st.session_state.time_window_selection = "6h"

time_window_options = ["1h", "3h", "6h", "24h", "Since Open"]
selected_window = st.selectbox("Time Window", time_window_options, 
                                index=time_window_options.index(st.session_state.time_window_selection),
                                key="biggest_movers_time_window")

# Update session state for sharing with dashboard
st.session_state.time_window_selection = selected_window

# Convert time window to timedelta and subtitle text
if selected_window == "Since Open":
    window_timedelta = None  # Special case - use all history
    window_label = "Since Open"
else:
    hours = int(selected_window.replace("h", ""))
    window_timedelta = timedelta(hours=hours)
    window_label = f"Last {selected_window}"

st.markdown(f'<p class="sub-header">Top 10 matches with largest odds movement ({window_label})</p>', unsafe_allow_html=True)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    st.error("Database connection not configured")
    st.stop()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

# Helper functions for implied probability calculations
def implied_prob(o):
    """Calculate implied probability from decimal odds"""
    if o and o > 1:
        return 1.0 / o
    return None

def delta_pp(open_o, now_o):
    """Calculate percentage point change in implied probability"""
    open_prob = implied_prob(open_o)
    now_prob = implied_prob(now_o)
    if open_prob is not None and now_prob is not None:
        return (now_prob - open_prob) * 100
    return None

def delta_odds_pct(open_o, now_o):
    """Calculate percentage change in odds"""
    if open_o and open_o > 0 and now_o and now_o > 0:
        return (now_o / open_o - 1) * 100
    return None

def implied_prob_pct_change(open_o, now_o):
    """Calculate percentage change in implied probability (not percentage points)"""
    open_prob = implied_prob(open_o)
    now_prob = implied_prob(now_o)
    if open_prob is not None and now_prob is not None and open_prob > 0:
        return ((now_prob - open_prob) / open_prob) * 100
    return None

def get_league_flag_html(league):
    """Get flag as HTML img tag using CDN"""
    LEAGUE_COUNTRY_CODES = {
        'EPL': 'GB',
        'Italy Serie A': 'IT',
        'Spain La Liga': 'ES',
        'Germany Bundesliga': 'DE',
        'France Ligue One': 'FR'
    }
    
    country_code = LEAGUE_COUNTRY_CODES.get(league, '')
    if country_code:
        flag_url = f"https://flagcdn.com/w20/{country_code.lower()}.png"
        return f'<img src="{flag_url}" alt="{country_code}" style="width: 20px; height: 15px; vertical-align: middle; margin-right: 4px; border: 1px solid rgba(255,255,255,0.2);">'
    return '⚽'

def get_biggest_movers(time_window=None):
    """Get the top 10 matches with largest absolute no-vig probability changes
    
    Args:
        time_window: timedelta object for time window, or None for "Since Open"
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate the cutoff time if window is specified
    if time_window is None:
        # "Since Open" - use all history, but still filter for recent matches only
        cutoff_time = None
    else:
        cutoff_time = datetime.now() - time_window
    
    # Get all unique matches within the window
    # Exclude finished and in-play matches - only include future matches (commence_time > NOW)
    if time_window is None:
        query = """
        SELECT DISTINCT league, home_team, away_team, bookmaker
        FROM odds
        WHERE timestamp >= NOW() - INTERVAL '7 days'
          AND commence_time IS NOT NULL 
          AND commence_time > NOW()
        """
        cursor.execute(query)
    else:
        query = """
        SELECT DISTINCT league, home_team, away_team, bookmaker
        FROM odds
        WHERE timestamp >= %s
          AND commence_time IS NOT NULL 
          AND commence_time > NOW()
        """
        cursor.execute(query, (cutoff_time,))
    
    matches = cursor.fetchall()
    
    movers = []
    
    for league, home_team, away_team, bookmaker in matches:
        # Get opening odds (first within the window, or earliest if "Since Open")
        if time_window is None:
            opening_query = """
            SELECT home_odds, away_odds, draw_odds, timestamp
            FROM odds
            WHERE league = %s 
              AND home_team = %s 
              AND away_team = %s
              AND bookmaker = %s
            ORDER BY timestamp ASC
            LIMIT 1
            """
            cursor.execute(opening_query, (league, home_team, away_team, bookmaker))
        else:
            opening_query = """
            SELECT home_odds, away_odds, draw_odds, timestamp
            FROM odds
            WHERE league = %s 
              AND home_team = %s 
              AND away_team = %s
              AND bookmaker = %s
              AND timestamp >= %s
            ORDER BY timestamp ASC
            LIMIT 1
            """
            cursor.execute(opening_query, (league, home_team, away_team, bookmaker, cutoff_time))
        
        opening_row = cursor.fetchone()
        
        # Get latest odds (must be within the window)
        if time_window is None:
            latest_query = """
            SELECT home_odds, away_odds, draw_odds, timestamp
            FROM odds
            WHERE league = %s 
              AND home_team = %s 
              AND away_team = %s
              AND bookmaker = %s
              AND timestamp >= NOW() - INTERVAL '7 days'
            ORDER BY timestamp DESC
            LIMIT 1
            """
            cursor.execute(latest_query, (league, home_team, away_team, bookmaker))
        else:
            latest_query = """
            SELECT home_odds, away_odds, draw_odds, timestamp
            FROM odds
            WHERE league = %s 
              AND home_team = %s 
              AND away_team = %s
              AND bookmaker = %s
              AND timestamp >= %s
            ORDER BY timestamp DESC
            LIMIT 1
            """
            cursor.execute(latest_query, (league, home_team, away_team, bookmaker, cutoff_time))
        
        latest_row = cursor.fetchone()
        
        if opening_row and latest_row:
            opening_home, opening_away, opening_draw, opening_time = opening_row
            latest_home, latest_away, latest_draw, latest_time = latest_row
            
            # Calculate implied probability deltas (Δpp) for each outcome
            home_delta_pp = delta_pp(opening_home, latest_home)
            draw_delta_pp = delta_pp(opening_draw, latest_draw)
            away_delta_pp = delta_pp(opening_away, latest_away)
            
            if all([home_delta_pp is not None, draw_delta_pp is not None, away_delta_pp is not None]):
                # Find the largest absolute delta_pp (for ranking - internal calculation)
                deltas = [
                    (abs(home_delta_pp), home_delta_pp, 'Home', opening_home, latest_home),
                    (abs(draw_delta_pp), draw_delta_pp, 'Draw', opening_draw, latest_draw),
                    (abs(away_delta_pp), away_delta_pp, 'Away', opening_away, latest_away)
                ]
                max_abs_delta_pp, signed_delta_pp, outcome, opening_odds, latest_odds = max(deltas, key=lambda x: x[0])
                
                # Calculate implied probability percentage change for display (not percentage points)
                prob_pct_change = implied_prob_pct_change(opening_odds, latest_odds)
                
                # Calculate minutes ago
                minutes_ago = int((datetime.now() - latest_time).total_seconds() / 60)
                
                movers.append({
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'outcome': outcome,
                    'delta_pp': signed_delta_pp,  # Keep for internal ranking
                    'abs_delta_pp': max_abs_delta_pp,  # Keep for internal ranking
                    'prob_pct_change': prob_pct_change,  # For display
                    'opening_odds': opening_odds,
                    'latest_odds': latest_odds,
                    'minutes_ago': minutes_ago
                })
    
    conn.close()
    
    # Sort by absolute delta_pp descending and return top 10
    movers.sort(key=lambda x: x['abs_delta_pp'], reverse=True)
    return movers[:10]

# Display Biggest Movers
movers = get_biggest_movers(window_timedelta)

if movers:
    for i, mover in enumerate(movers):
        league = mover['league']
        home = mover['home_team']
        away = mover['away_team']
        outcome = mover['outcome']
        opening_odds = mover['opening_odds']
        latest_odds = mover['latest_odds']
        prob_pct_change = mover.get('prob_pct_change', None)
        minutes_ago = mover['minutes_ago']
        
        # Get league flag
        league_flag_html = get_league_flag_html(league)
        league_name = "Premier League" if league == 'EPL' else league.replace('Italy ', '').replace('Spain ', '').replace('Germany ', '').replace('France ', '')
        
        # Determine if odds shortened or drifted
        if latest_odds < opening_odds:
            movement_text = "shortened"
            movement_color = "#44ff44"  # Green
        else:
            movement_text = "drifted"
            movement_color = "#ff4444"  # Red
        
        # Calculate implied probabilities
        start_prob = implied_prob(opening_odds)
        current_prob = implied_prob(latest_odds)
        
        # Calculate delta (percentage point change) for strength label
        abs_delta_pp = None
        if start_prob is not None and current_prob is not None:
            delta = (current_prob - start_prob) * 100
            abs_delta_pp = abs(delta)
            start_prob_pct = start_prob * 100
            current_prob_pct = current_prob * 100
            delta_formatted = f"{delta:+.1f}%"
        else:
            delta = None
            start_prob_pct = None
            current_prob_pct = None
            delta_formatted = ""
        
        # Determine strength badge
        strength_badge = ""
        if abs_delta_pp is not None:
            if abs_delta_pp >= 5:
                strength_badge = '<span class="strength-badge strong">Strong</span>'
            elif abs_delta_pp >= 3:
                strength_badge = '<span class="strength-badge medium">Medium</span>'
        
        # Format time display
        if minutes_ago < 1:
            time_display = "just now"
        else:
            time_display = f"{minutes_ago}m ago"
        
        # Line 1 (primary): "{Side} — shortened/drifted ({start_odds} → {current_odds})"
        line1 = f'{outcome} — <span style="color: {movement_color}; font-weight: 600;">{movement_text}</span> ({opening_odds:.2f} → {latest_odds:.2f}){strength_badge}'
        
        # Line 2 (secondary, muted): "Implied chance: {start%} → {current%} ({delta%}) · Updated {time}"
        if start_prob_pct is not None and current_prob_pct is not None:
            line2 = f"Implied chance: {start_prob_pct:.1f}% → {current_prob_pct:.1f}% ({delta_formatted}) · Updated {time_display}"
        else:
            line2 = f"Updated {time_display}"
        
        # Create modern card row with new formatting
        row_html = f"""
        <div class="mover-card">
            <div class="mover-match">{home} vs {away} ({league_flag_html} {league_name})</div>
            <div class="mover-line-primary">{line1}</div>
            <div class="mover-line-secondary">{line2}</div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
else:
    st.info("No movement data available yet.")
