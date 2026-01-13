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

# Custom CSS for branding and segmented control with modern typography
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
    
    /* Modern expander/card styling */
    .stExpander {
        margin-bottom: 16px;
    }
    
    .stExpander summary {
        padding: 16px 20px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(0, 0, 0, 0.25) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stExpander summary:hover {
        background-color: rgba(0, 0, 0, 0.35) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 6px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stExpander > div {
        border-radius: 0 0 14px 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: none !important;
        background-color: rgba(0, 0, 0, 0.15) !important;
        padding: 20px 24px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Remove heavy dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 2.5rem 0;
    }
    
    /* Increase spacing between sections */
    .element-container {
        margin-bottom: 2rem;
    }
    
    /* Modern subheader styling */
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 1.5rem !important;
        margin-top: 2rem !important;
    }
    
    /* Modern table styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Responsive odds display */
    .odds-table-container {
        width: 100%;
    }
    
    /* Desktop: show table, hide cards */
    .odds-table-desktop {
        display: table;
        width: 100%;
        border-collapse: collapse;
    }
    
    .odds-cards-mobile {
        display: none;
    }
    
    /* Mobile card styling */
    .odds-card-mobile {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .odds-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .odds-card-header strong {
        color: #ffffff;
        font-size: 1rem;
    }
    
    .odds-card-updated {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
    }
    
    .odds-card-body {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .odds-card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
    }
    
    .odds-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .odds-value {
        color: #ffffff;
        font-size: 0.95rem;
        text-align: right;
    }
    
    /* Mobile responsive: hide table, show cards */
    @media screen and (max-width: 768px) {
        .odds-table-desktop {
            display: none !important;
        }
        
        .odds-cards-mobile {
            display: block !important;
        }
        
        /* Adjust main content for mobile */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Adjust header for mobile */
        .main-header {
            font-size: 2rem !important;
        }
        
        .sub-header {
            font-size: 1.1rem !important;
        }
        
        /* Adjust expander padding for mobile */
        .stExpander > div {
            padding: 16px !important;
        }
    }
    
    /* Compact status text */
    .status-text {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.5);
        text-align: right;
        margin-top: 0.5rem;
        margin-bottom: 0;
        padding-top: 0;
    }
    
    /* Constrain main content column width and center it */
    .main .block-container {
        padding-top: 1rem !important;
        max-width: 1150px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Reduce spacing after header */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Biggest Movers card styling */
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
    
    /* Ensure flag emojis render properly */
    .flag-emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Android Emoji", "EmojiSymbols", "EmojiOne Mozilla", "Twemoji Mozilla", "Segoe UI Symbol", sans-serif;
        font-size: 1.2em;
        display: inline-block;
        line-height: 1;
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
    
    /* Style league selection buttons in sidebar */
    .stSidebar button[kind="secondary"] {
        width: 100% !important;
        text-align: left !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSidebar button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Sidebar navigation icons styling */
    .nav-icon {
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        opacity: 0.7;
        flex-shrink: 0;
    }
    
    section[data-testid="stSidebar"] nav a,
    section[data-testid="stSidebar"] a[href] {
        display: flex !important;
        align-items: center !important;
    }
    
    section[data-testid="stSidebar"] nav a:hover .nav-icon,
    section[data-testid="stSidebar"] a:hover .nav-icon {
        opacity: 1;
    }
    
    /* CSS fallback for Dashboard icon using ::before */
    section[data-testid="stSidebar"] nav a[href="/"]::before,
    section[data-testid="stSidebar"] nav a[href=""]::before {
        content: '';
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.7)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.7;
        flex-shrink: 0;
    }
    
    /* CSS fallback for Biggest Movers icon */
    section[data-testid="stSidebar"] nav a[href*="Biggest_Movers"]::before,
    section[data-testid="stSidebar"] nav a[href*="biggest"]::before {
        content: '';
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.7)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.7;
        flex-shrink: 0;
    }
    </style>
    <script>
    // Add icons to sidebar navigation and capitalize Dashboard
    function addNavIcons() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (!sidebar) {
            // Try alternative selector
            setTimeout(addNavIcons, 100);
            return;
        }
        
        // Find all navigation links - try multiple selectors
        let navLinks = sidebar.querySelectorAll('nav a');
        if (navLinks.length === 0) {
            navLinks = sidebar.querySelectorAll('a[href]');
        }
        if (navLinks.length === 0) {
            navLinks = sidebar.querySelectorAll('[data-testid*="nav"] a, [class*="nav"] a');
        }
        
        navLinks.forEach(link => {
            // Skip if icon already added
            if (link.querySelector('.nav-icon')) return;
            
            const text = link.textContent.trim();
            const href = link.getAttribute('href') || '';
            const textLower = text.toLowerCase();
            
            let iconSvg = '';
            let shouldCapitalize = false;
            
            // Dashboard icon (grid/layout) - check for dashboard (case insensitive)
            if (textLower === 'dashboard' || href === '/' || href === '' || href === '/dashboard' || href.includes('dashboard')) {
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>';
                shouldCapitalize = true;
            }
            // Biggest Movers icon (trending up)
            else if (textLower.includes('biggest movers') || textLower.includes('biggest_movers') || href.includes('Biggest_Movers') || href.includes('biggest')) {
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>';
            }
            
            if (iconSvg) {
                const icon = document.createElement('span');
                icon.className = 'nav-icon';
                icon.innerHTML = iconSvg;
                link.insertBefore(icon, link.firstChild);
            }
            
            // Capitalize Dashboard text
            if (shouldCapitalize && textLower === 'dashboard') {
                const textNode = Array.from(link.childNodes).find(node => node.nodeType === 3);
                if (textNode) {
                    textNode.textContent = 'Dashboard';
                } else {
                    // If no direct text node, try to update the text content
                    const currentText = link.textContent.trim();
                    if (currentText.toLowerCase() === 'dashboard') {
                        link.innerHTML = link.innerHTML.replace(/dashboard/gi, 'Dashboard');
                    }
                }
            }
        });
    }
    
    // Run immediately and on load
    addNavIcons();
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addNavIcons);
    }
    
    // Re-run after Streamlit navigation (using MutationObserver)
    setTimeout(() => {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            const observer = new MutationObserver(() => {
                setTimeout(addNavIcons, 50);
            });
            observer.observe(sidebar, { childList: true, subtree: true });
        }
    }, 500);
    
    // Also run after a delay to catch late-rendered elements
    setTimeout(addNavIcons, 1000);
    setTimeout(addNavIcons, 2000);
    </script>
""", unsafe_allow_html=True)

# Header with compact status
header_col1, header_col2 = st.columns([0.7, 0.3])
with header_col1:
    st.markdown('<p class="main-header">⚽ OddsEdge</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Soccer Betting Odds Tracker</p>', unsafe_allow_html=True)
with header_col2:
    # Status placeholder - will be updated after odds_data loads
    status_placeholder = st.empty()

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

# League to country code mapping for flag images
LEAGUE_COUNTRY_CODES = {
    'EPL': 'GB',
    'Italy Serie A': 'IT',
    'Spain La Liga': 'ES',
    'Germany Bundesliga': 'DE',
    'France Ligue One': 'FR'
}

def get_league_flag_html(league):
    """Get flag as HTML img tag using CDN"""
    country_code = LEAGUE_COUNTRY_CODES.get(league, '')
    if country_code:
        # Using flagcdn.com CDN for reliable flag images
        flag_url = f"https://flagcdn.com/w20/{country_code.lower()}.png"
        return f'<img src="{flag_url}" alt="{country_code}" style="width: 20px; height: 15px; vertical-align: middle; margin-right: 4px; border: 1px solid rgba(255,255,255,0.2);">'
    return '⚽'  # Fallback to soccer ball emoji

# League navigation mapping (database name -> display name with flag)
# Using HTML img tags for flags in sidebar
LEAGUE_DISPLAY_NAMES = {
    None: '🌍 All Leagues',
    'EPL': f"{get_league_flag_html('EPL')} Premier League",
    'Italy Serie A': f"{get_league_flag_html('Italy Serie A')} Serie A",
    'Spain La Liga': f"{get_league_flag_html('Spain La Liga')} La Liga",
    'Germany Bundesliga': f"{get_league_flag_html('Germany Bundesliga')} Bundesliga",
    'France Ligue One': f"{get_league_flag_html('France Ligue One')} Ligue 1"
}

def get_league_flag(league):
    """Get flag HTML for a league (for use in markdown)"""
    return get_league_flag_html(league)

# Supported leagues (always show all, even if 0 matches)
SUPPORTED_LEAGUES = ['EPL', 'Italy Serie A', 'Spain La Liga', 'Germany Bundesliga', 'France Ligue One']

# Load current odds
odds_data = load_latest_odds()

# League navigation in sidebar
# Initialize session state for selected league
if 'selected_league' not in st.session_state:
    st.session_state.selected_league = None

st.sidebar.markdown("### Leagues")

# Display clickable league options with flags
for league in [None] + SUPPORTED_LEAGUES:
    if league is None:
        # All Leagues option
        is_selected = st.session_state.selected_league is None
        # Use columns to display flag and button
        col1, col2 = st.sidebar.columns([0.15, 0.85])
        with col1:
            st.markdown("🌍")
        with col2:
            if st.button("All Leagues", key=f"league_{league}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_league = None
                st.rerun()
    else:
        # Individual league options
        flag_html = get_league_flag_html(league)
        league_name = "Premier League" if league == 'EPL' else league.replace('Italy ', '').replace('Spain ', '').replace('Germany ', '').replace('France ', '')
        is_selected = st.session_state.selected_league == league
        
        # Use columns to display flag and button
        col1, col2 = st.sidebar.columns([0.15, 0.85])
        with col1:
            st.markdown(flag_html, unsafe_allow_html=True)
        with col2:
            if st.button(league_name, key=f"league_{league}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_league = league
                st.rerun()

# Get the selected league value
selected_league = st.session_state.selected_league

# Update status text
if odds_data:
    latest_update = max(row[7] for row in odds_data)
    minutes_ago = int((datetime.now() - latest_update).total_seconds() / 60)
    status_placeholder.markdown(f'<div class="status-text">Feed active · updated {minutes_ago}m ago</div>', unsafe_allow_html=True)
else:
    status_placeholder.markdown('<div class="status-text">Feed active · no data</div>', unsafe_allow_html=True)

if not odds_data:
    st.warning("No odds data available yet. The data collector may still be gathering initial data.")
    st.info("Check back in a few minutes, or verify that the data collector is running.")
else:
    # Apply league filter
    filtered_data = odds_data
    if selected_league is not None:
        filtered_data = [row for row in filtered_data if row[0] == selected_league]
    
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
        
        # Add spacing after date header
        st.markdown("<br>", unsafe_allow_html=True)
        
        for (league, home, away), match_data in matches_by_date[match_date].items():
            league_flag_html = get_league_flag(league)
            # Create a container with flag and expander
            flag_col, expander_col = st.columns([0.05, 0.95])
            with flag_col:
                st.markdown(league_flag_html, unsafe_allow_html=True)
            with expander_col:
                with st.expander(f"{home} vs {away} ({league})", expanded=False):
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
                    
                    # Create HTML table for desktop and cards for mobile
                    html_table = "<div class='odds-table-container'>"
                    html_table += "<table class='odds-table-desktop' style='width: 100%; border-collapse: collapse;'>"
                    html_table += "<thead><tr style='border-bottom: 2px solid rgba(255,255,255,0.2);'>"
                    html_table += "<th style='text-align: left; padding: 8px;'>Bookmaker</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Home</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Draw</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Away</th>"
                    html_table += "<th style='text-align: right; padding: 8px;'>Updated</th>"
                    html_table += "</tr></thead><tbody>"
                    
                    # Mobile cards container
                    html_table += "<div class='odds-cards-mobile'>"
                    
                    for row_data in table_rows:
                        # Desktop table row
                        html_table += "<tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>"
                        html_table += f"<td style='padding: 8px;'><strong>{row_data['Bookmaker']}</strong></td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Home']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Draw']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Away']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: right;'>{row_data['Updated']}</td>"
                        html_table += "</tr>"
                        
                        # Mobile card
                        html_table += f"""
                        <div class='odds-card-mobile'>
                            <div class='odds-card-header'>
                                <strong>{row_data['Bookmaker']}</strong>
                                <span class='odds-card-updated'>{row_data['Updated']}</span>
                            </div>
                            <div class='odds-card-body'>
                                <div class='odds-card-row'>
                                    <span class='odds-label'>Home:</span>
                                    <span class='odds-value'>{row_data['Home']}</span>
                                </div>
                                <div class='odds-card-row'>
                                    <span class='odds-label'>Draw:</span>
                                    <span class='odds-value'>{row_data['Draw']}</span>
                                </div>
                                <div class='odds-card-row'>
                                    <span class='odds-label'>Away:</span>
                                    <span class='odds-value'>{row_data['Away']}</span>
                                </div>
                            </div>
                        </div>
                        """
                    
                    html_table += "</div>"  # Close mobile cards container
                    html_table += "</tbody></table>"  # Close desktop table
                    html_table += "</div>"  # Close odds-table-container
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
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Page will refresh every 60 seconds")
        import time
        time.sleep(60)
        st.rerun()

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking | Data updates every 15 minutes")