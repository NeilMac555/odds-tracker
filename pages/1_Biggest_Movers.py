import streamlit as st
import psycopg2
from datetime import datetime
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
        margin-bottom: 3rem;
        font-weight: 400;
        letter-spacing: -0.01em;
    }
    
    /* Modern card styling */
    .mover-card {
        padding: 20px 24px;
        margin-bottom: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(0, 0, 0, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .mover-card:hover {
        background-color: rgba(0, 0, 0, 0.35);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 6px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .mover-match {
        font-size: 1.15rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    
    .mover-details {
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.95rem;
        margin-top: 6px;
        display: inline-block;
        line-height: 1.6;
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
    </style>
""", unsafe_allow_html=True)

# Hero Header Section
st.markdown('<p class="main-header">📊 Biggest Movers</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Top 10 matches with largest odds movement (Last 24h)</p>', unsafe_allow_html=True)

# Add spacing
st.markdown("<br>", unsafe_allow_html=True)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    st.error("Database connection not configured")
    st.stop()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def calculate_no_vig_probability(home_odds, draw_odds, away_odds):
    """Calculate no-vig implied probabilities from decimal odds"""
    if not all([home_odds, draw_odds, away_odds]):
        return None, None, None
    
    # Calculate implied probabilities (1/odds)
    home_implied = 1.0 / home_odds
    draw_implied = 1.0 / draw_odds
    away_implied = 1.0 / away_odds
    
    # Total market margin (vig)
    total_implied = home_implied + draw_implied + away_implied
    
    # Remove vig by normalizing
    home_no_vig = home_implied / total_implied
    draw_no_vig = draw_implied / total_implied
    away_no_vig = away_implied / total_implied
    
    return home_no_vig, draw_no_vig, away_no_vig

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

def get_biggest_movers():
    """Get the top 10 matches with largest absolute no-vig probability changes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all unique matches from last 24 hours
    query = """
    SELECT DISTINCT league, home_team, away_team, bookmaker
    FROM odds
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
      AND commence_time IS NOT NULL 
      AND commence_time >= CURRENT_DATE 
      AND commence_time < CURRENT_DATE + INTERVAL '3 days'
    """
    
    cursor.execute(query)
    matches = cursor.fetchall()
    
    movers = []
    
    for league, home_team, away_team, bookmaker in matches:
        # Get opening odds (first in last 24h)
        opening_query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
          AND home_team = %s 
          AND away_team = %s
          AND bookmaker = %s
          AND timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp ASC
        LIMIT 1
        """
        
        cursor.execute(opening_query, (league, home_team, away_team, bookmaker))
        opening_row = cursor.fetchone()
        
        # Get latest odds
        latest_query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
          AND home_team = %s 
          AND away_team = %s
          AND bookmaker = %s
          AND timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        cursor.execute(latest_query, (league, home_team, away_team, bookmaker))
        latest_row = cursor.fetchone()
        
        if opening_row and latest_row:
            opening_home, opening_away, opening_draw, opening_time = opening_row
            latest_home, latest_away, latest_draw, latest_time = latest_row
            
            # Calculate no-vig probabilities
            opening_home_nv, opening_draw_nv, opening_away_nv = calculate_no_vig_probability(
                opening_home, opening_draw, opening_away
            )
            latest_home_nv, latest_draw_nv, latest_away_nv = calculate_no_vig_probability(
                latest_home, latest_draw, latest_away
            )
            
            if all([opening_home_nv, opening_draw_nv, opening_away_nv, 
                   latest_home_nv, latest_draw_nv, latest_away_nv]):
                # Calculate deltas (percentage point change)
                home_delta = (latest_home_nv - opening_home_nv) * 100
                draw_delta = (latest_draw_nv - opening_draw_nv) * 100
                away_delta = (latest_away_nv - opening_away_nv) * 100
                
                # Find the largest absolute delta
                deltas = [
                    (abs(home_delta), home_delta, 'Home', opening_home, latest_home),
                    (abs(draw_delta), draw_delta, 'Draw', opening_draw, latest_draw),
                    (abs(away_delta), away_delta, 'Away', opening_away, latest_away)
                ]
                max_abs_delta, signed_delta, outcome, opening_odds, latest_odds = max(deltas, key=lambda x: x[0])
                
                # Calculate minutes ago
                minutes_ago = int((datetime.now() - latest_time).total_seconds() / 60)
                
                movers.append({
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'outcome': outcome,
                    'delta_pct': signed_delta,
                    'abs_delta': max_abs_delta,
                    'opening_odds': opening_odds,
                    'latest_odds': latest_odds,
                    'minutes_ago': minutes_ago
                })
    
    conn.close()
    
    # Sort by absolute delta descending and return top 10
    movers.sort(key=lambda x: x['abs_delta'], reverse=True)
    return movers[:10]

# Display Biggest Movers
movers = get_biggest_movers()

if movers:
    for i, mover in enumerate(movers):
        league = mover['league']
        home = mover['home_team']
        away = mover['away_team']
        outcome = mover['outcome']
        delta_pct = mover['delta_pct']
        minutes_ago = mover['minutes_ago']
        
        # Get league flag
        league_flag_html = get_league_flag_html(league)
        league_name = "Premier League" if league == 'EPL' else league.replace('Italy ', '').replace('Spain ', '').replace('Germany ', '').replace('France ', '')
        
        # Get opening and latest odds for the moved outcome
        opening_odds = mover['opening_odds']
        latest_odds = mover['latest_odds']
        
        # Format odds change with betting semantics:
        # - Odds decreased (e.g., 2.20 → 1.90): "Odds shortening" with green text and down arrow (↓)
        # - Odds increased (e.g., 2.10 → 2.30): "Odds drifting" with red text and up arrow (↑)
        if latest_odds < opening_odds:
            # Odds decreased (shortening) - green text, down arrow
            status_text = "Odds shortening"
            status_color = "#44ff44"  # Green
            arrow = "↓"
            odds_display = f"{opening_odds:.2f} → {latest_odds:.2f}"
        else:
            # Odds increased (drifting) - red text, up arrow
            status_text = "Odds drifting"
            status_color = "#ff4444"  # Red
            arrow = "↑"
            odds_display = f"{opening_odds:.2f} → {latest_odds:.2f}"
        
        # Create modern card row
        row_html = f"""
        <div class="mover-card">
            <div class="mover-match">{home} vs {away} ({league_flag_html} {league_name})</div>
            <div class="mover-details">{outcome} · <span style="color: {status_color}; font-weight: 600; font-size: 1.05em;">{arrow} {status_text} ({odds_display})</span> · Updated {minutes_ago}m ago</div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
else:
    st.info("No movement data available yet.")
