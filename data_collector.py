import requests
import psycopg2
import time
import os
from datetime import datetime

# Configuration
API_KEY = os.environ.get('ODDS_API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

if not API_KEY:
    print("ERROR: ODDS_API_KEY not found in environment variables")
    exit(1)

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

SPORT = 'soccer'
REGIONS = 'eu'
MARKETS = 'h2h'
ODDS_FORMAT = 'decimal'

# Leagues to track
LEAGUES = [
    'soccer_epl',          # English Premier League
    'soccer_spain_la_liga', # La Liga
    'soccer_germany_bundesliga', # Bundesliga
    'soccer_italy_serie_a', # Serie A
    'soccer_france_ligue_one' # Ligue 1
]

# Only track Pinnacle
PINNACLE_BOOKMAKER = 'Pinnacle'

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def fetch_odds(league):
    """Fetch odds from The Odds API"""
    url = f'https://api.the-odds-api.com/v4/sports/{league}/odds/'
    
    params = {
        'apiKey': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds for {league}: {e}")
        return None

def save_odds(data, league_name):
    """Save odds to database - ONLY Pinnacle"""
    if not data:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved_count = 0
    
    for game in data:
        home_team = game['home_team']
        away_team = game['away_team']
        
        for bookmaker in game.get('bookmakers', []):
            bookmaker_name = bookmaker['title']
            
            # ONLY save Pinnacle odds
            if bookmaker_name != PINNACLE_BOOKMAKER:
                continue
            
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    outcomes = market['outcomes']
                    
                    # Find home, away, and draw odds
                    home_odds = None
                    away_odds = None
                    draw_odds = None
                    
                    for outcome in outcomes:
                        if outcome['name'] == home_team:
                            home_odds = outcome['price']
                        elif outcome['name'] == away_team:
                            away_odds = outcome['price']
                        elif outcome['name'] == 'Draw':
                            draw_odds = outcome['price']
                    
                    # Only save if we have all three odds
                    if home_odds and away_odds and draw_odds:
                        cursor.execute('''
                        INSERT INTO odds (league, home_team, away_team, bookmaker, 
                                        home_odds, away_odds, draw_odds, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (league_name, home_team, away_team, bookmaker_name,
                              home_odds, away_odds, draw_odds, datetime.now()))
                        saved_count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return saved_count

def collect_all_odds():
    """Collect odds from all configured leagues"""
    print(f"[{datetime.now().isoformat()}] Collecting odds...")
    
    total_saved = 0
    
    for league in LEAGUES:
        league_name = league.replace('soccer_', '').replace('_', ' ').title()
        data = fetch_odds(league)
        
        if data:
            saved = save_odds(data, league_name)
            total_saved += saved
            print(f"✅ {league_name}: {saved} Pinnacle matches saved")
        else:
            print(f"❌ {league_name}: Failed to fetch data")
    
    print(f"[{datetime.now().isoformat()}] Collection complete!")
    return total_saved

if __name__ == '__main__':
    print("🚀 Starting Odds Collector (Pinnacle only)...")
    
    # Run initial collection
    collect_all_odds()
    
    # Continue collecting every 15 minutes
    print("\n📊 Collecting Pinnacle odds every 15 minutes. Press Ctrl+C to stop.\n")
    
    while True:
        time.sleep(900)  # 15 minutes
        collect_all_odds()
