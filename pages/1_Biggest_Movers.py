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

# Custom CSS
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
st.markdown('<p class="main-header">📊 Biggest Movers</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Top 10 matches with largest odds movement (Last 24h)</p>', unsafe_allow_html=True)

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
                    (abs(home_delta), home_delta, 'Home'),
                    (abs(draw_delta), draw_delta, 'Draw'),
                    (abs(away_delta), away_delta, 'Away')
                ]
                max_abs_delta, signed_delta, outcome = max(deltas, key=lambda x: x[0])
                
                # Calculate minutes ago
                minutes_ago = int((datetime.now() - latest_time).total_seconds() / 60)
                
                movers.append({
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'outcome': outcome,
                    'delta_pct': signed_delta,
                    'abs_delta': max_abs_delta,
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
        
        # Format delta with sign, color, and arrow
        # Betting semantics:
        # - Odds shortened (probability increased) = green up arrow (team more likely)
        # - Odds drifted (probability decreased) = red down arrow (team less likely)
        if delta_pct > 0:
            # Probability increased (odds shortened) - green up arrow
            delta_sign = "+"
            delta_color = "#44ff44"  # Green
            arrow = "▲"
            delta_display = f"{arrow} {delta_sign}{abs(delta_pct):.2f}%"
        else:
            # Probability decreased (odds drifted) - red down arrow
            delta_sign = "−"
            delta_color = "#ff4444"  # Red
            arrow = "▼"
            delta_display = f"{arrow} {delta_sign}{abs(delta_pct):.2f}%"
        
        # Create row
        row_html = f"""
        <div style="padding: 12px 16px; margin-bottom: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1); background-color: rgba(0,0,0,0.2);">
            <strong style="font-size: 1.1em;">{home} vs {away}</strong> ({league_flag_html} {league_name})<br>
            <span style="color: rgba(255,255,255,0.7); font-size: 0.95em; margin-top: 4px; display: inline-block;">{outcome} <span style="color: {delta_color}; font-weight: bold;">{delta_display}</span> · Updated {minutes_ago}m ago</span>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
else:
    st.info("No movement data available yet.")
