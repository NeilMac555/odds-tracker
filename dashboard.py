import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

import os
API_KEY = os.getenv('ODDS_API_KEY', 'bc5c2e6fce5dc1683f0267a02e8afe05')

st.set_page_config(
    page_title="Odds Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .main { background: linear-gradient(to bottom, #000000, #0a0a0a); padding: 3rem 4rem; }
    #MainMenu, footer, header {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 700 !important; font-size: 2.5rem !important; }
    .subtitle { color: #8e8e93; font-size: 1.1rem; margin-bottom: 3rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.75rem; border-bottom: 1px solid #1c1c1e; margin-bottom: 2rem; }
    .stTabs [data-baseweb="tab"] { background: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 12px; padding: 0.75rem 1.5rem; color: #8e8e93; transition: all 0.3s; }
    .stTabs [data-baseweb="tab"]:hover { background: #2c2c2e; transform: translateY(-1px); }
    .stTabs [aria-selected="true"] { background: #ffffff; color: #000000; }
    .stExpander { background: #1c1c1e !important; border: 1px solid #2c2c2e !important; border-radius: 16px !important; margin-bottom: 1rem !important; }
    .stExpander:hover { border-color: #3a3a3c !important; transform: translateY(-2px) !important; }
    .change-positive { color: #34c759; font-weight: 600; }
    .change-negative { color: #ff3b30; font-weight: 600; }
    .change-neutral { color: #8e8e93; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

st.markdown("# Odds Tracker")
st.markdown('<p class="subtitle">Real-time odds monitoring with price movement trends</p>', unsafe_allow_html=True)

league_map = {
    "Premier League": "soccer_epl",
    "La Liga": "soccer_spain_la_liga",
    "Bundesliga": "soccer_germany_bundesliga",
    "Serie A": "soccer_italy_serie_a",
    "Ligue 1": "soccer_france_ligue_one"
}

# Filter for most popular lines
POPULAR_TOTALS = [2.25, 2.5, 3.0]  # Cover low and high scoring matches
POPULAR_AH_POINTS = [-1.0, -0.5, 0, 0.5, 1.0]

@st.cache_data(ttl=300)
def get_odds(sport_key):
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'h2h,spreads,totals', 'oddsFormat': 'decimal'}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def get_odds_history(match_id, market_type):
    conn = sqlite3.connect('odds_tracker.db')
    query = "SELECT timestamp, outcome_name, price, point FROM odds_history WHERE match_id = ? AND market = ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn, params=(match_id, market_type))
    conn.close()
    return df

def filter_popular_lines(df, market_type):
    """Filter to show only popular lines"""
    if market_type == 'totals':
        df = df[df['point'].isin(POPULAR_TOTALS)]
    elif market_type == 'spreads':
        df = df[df['point'].isin(POPULAR_AH_POINTS)]
    return df

def calculate_price_changes(match_id, market_type):
    df = get_odds_history(match_id, market_type)
    if df.empty:
        return {}
    
    df = filter_popular_lines(df, market_type)
    changes = {}
    
    for _, group in df.groupby(['outcome_name', 'point']):
        if len(group) < 2:
            continue
            
        outcome = group.iloc[0]['outcome_name']
        point = group.iloc[0]['point']
        opening = group.iloc[0]['price']
        current = group.iloc[-1]['price']
        pct_change = ((current - opening) / opening) * 100
        
        # Create clear label
        if market_type == 'spreads':
            label = f"{outcome} ({point:+.2f})"
        elif market_type == 'totals':
            label = f"{outcome} {point:.1f}"
        else:
            label = outcome
        
        changes[label] = {
            'opening': opening,
            'current': current,
            'change_pct': pct_change,
            'outcome': outcome,
            'point': point
        }
    
    return changes

def create_trend_chart(match_id, market_type, title, changes):
    df = get_odds_history(match_id, market_type)
    if df.empty:
        return None
    
    df = filter_popular_lines(df, market_type)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = go.Figure()
    
    for label, change_info in changes.items():
        outcome = change_info['outcome']
        point = change_info['point']
        
        # Filter data for this specific outcome+point combo
        mask = (df['outcome_name'] == outcome) & (df['point'] == point)
        outcome_data = df[mask]
        
        if outcome_data.empty:
            continue
        
        avg_prices = outcome_data.groupby('timestamp')['price'].mean().reset_index()
        pct = change_info['change_pct']
        legend_text = f"{label} ({pct:+.1f}%)"
        
        fig.add_trace(go.Scatter(
            x=avg_prices['timestamp'], 
            y=avg_prices['price'],
            mode='lines+markers', 
            name=legend_text, 
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title=title, 
        xaxis_title="Time", 
        yaxis_title="Odds", 
        template="plotly_dark", 
        height=350,
        showlegend=True
    )
    return fig

tabs = st.tabs(list(league_map.keys()))

for idx, (league_name, sport_key) in enumerate(league_map.items()):
    with tabs[idx]:
        matches = get_odds(sport_key)
        
        if matches:
            col1, col2, col3 = st.columns(3)
            col1.metric("Matches", len(matches))
            col2.metric("League", league_name)
            col3.metric("Updated", datetime.now().strftime("%H:%M"))
            st.markdown("---")
            
            for match in matches:
                with st.expander(f"⚽  {match['home_team']} vs {match['away_team']}", expanded=False):
                    
                    st.markdown("### 📈 Price Trends")
                    
                    h2h_changes = calculate_price_changes(match['id'], 'h2h')
                    ah_changes = calculate_price_changes(match['id'], 'spreads')
                    totals_changes = calculate_price_changes(match['id'], 'totals')
                    
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        chart = create_trend_chart(match['id'], 'h2h', '1X2', h2h_changes)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True, key=f"h2h_{match['id']}")
                            st.markdown("**Movement:**")
                            for label, data in h2h_changes.items():
                                pct = data['change_pct']
                                color_class = 'change-positive' if pct > 0 else 'change-negative' if pct < 0 else 'change-neutral'
                                st.markdown(f'<span class="{color_class}">{label}: {pct:+.2f}%</span>', unsafe_allow_html=True)
                        else:
                            st.info("Collecting data...")
                    
                    with c2:
                        chart = create_trend_chart(match['id'], 'spreads', 'Asian Handicap (Popular Lines)', ah_changes)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True, key=f"ah_{match['id']}")
                            st.markdown("**Movement:**")
                            for label, data in ah_changes.items():
                                pct = data['change_pct']
                                color_class = 'change-positive' if pct > 0 else 'change-negative' if pct < 0 else 'change-neutral'
                                st.markdown(f'<span class="{color_class}">{label}: {pct:+.2f}%</span>', unsafe_allow_html=True)
                        else:
                            st.info("Collecting data...")
                    
                    with c3:
                        chart = create_trend_chart(match['id'], 'totals', 'Total Goals', totals_changes)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True, key=f"totals_{match['id']}")
                            st.markdown("**Movement:**")
                            for label, data in totals_changes.items():
                                pct = data['change_pct']
                                color_class = 'change-positive' if pct > 0 else 'change-negative' if pct < 0 else 'change-neutral'
                                st.markdown(f'<span class="{color_class}">{label}: {pct:+.2f}%</span>', unsafe_allow_html=True)
                        else:
                            st.info("Collecting data...")
                    
                    st.markdown("---")
                    st.markdown("### 💰 Current Odds (Popular Lines)")
                    
                    for bookmaker in match.get('bookmakers', []):
                        if bookmaker['key'] == 'pinnacle':
                            st.markdown(f"**{bookmaker['title']}**")
                            
                            for market in bookmaker['markets']:
                                if market['key'] == 'h2h':
                                    st.write("1X2:")
                                    for outcome in market['outcomes']:
                                        st.write(f"  {outcome['name']}: {outcome['price']:.2f}")
                                
                                elif market['key'] == 'spreads':
                                    st.write("Asian Handicap (Popular):")
                                    for outcome in market['outcomes']:
                                        point = outcome.get('point', 0)
                                        if point in POPULAR_AH_POINTS:
                                            st.write(f"  {outcome['name']} ({point:+.2f}): {outcome['price']:.2f}")
                                
                                elif market['key'] == 'totals':
                                    st.write("Total Goals (O/U 2.5):")
                                    for outcome in market['outcomes']:
                                        point = outcome.get('point', 0)
                                        if point == 2.5:
                                            st.write(f"  {outcome['name']} {point:.1f}: {outcome['price']:.2f}")
                            st.markdown("")
        else:
            st.info("No matches found")