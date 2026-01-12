import requests
import psycopg2
import os
import time
from datetime import datetime

# Configuration
API_KEY = os.environ.get('ODDS_API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Leagues to track
LEAGUES = {
    'soccer_epl': 'EPL',
    'soccer_spain_la_liga': 'Spain La Liga',
    'soccer_germany_bundesliga': 'Germany Bundesliga',
    'soccer_italy_serie_a': 'Italy Serie A',
    'soccer_france_ligue_one': 'France Ligue One'
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def fetch_odds(league_key):
    """Fetch odds from The Odds API for a specific league"""
    url = f"https://api.the-odds-api.com/v4/sports/{league_key}/odds"
    
    params = {
        'apiKey': API_KEY,
        'regions': 'us,uk,eu',
        'markets': 'h2h',
        'oddsFormat': 'decimal',
        'bookmakers': 'pinnacle'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {league_key}: {e}")
        return []

def save_odds(odds_data, league_name):
    """Save odds to database"""
    if not odds_data:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved_count = 0
    
    for match in odds_data:
        home_team = match.get('home_team')
        away_team = match.get('away_team')
        commence_time = match.get('commence_time')  # NEW: Get match kickoff time
        
        # Convert ISO string to datetime
        if commence_time:
            commence_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
        
        for bookmaker in match.get('bookmakers', []):
            bookmaker_name = bookmaker.get('key')
            
            # Only process Pinnacle
            if bookmaker_name != 'pinnacle':
                continue
            
            for market in bookmaker.get('markets', []):
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    
                    # Extract odds
                    home_odds = None
                    away_odds = None
                    draw_odds = None
                    
                    for outcome in outcomes:
                        if outcome.get('name') == home_team:
                            home_odds = outcome.get('price')
                        elif outcome.get('name') == away_team:
                            away_odds = outcome.get('price')
                        elif outcome.get('name') == 'Draw':
                            draw_odds = outcome.get('price')
                    
                    # Insert into database
                    if home_odds and away_odds:
                        cursor.execute("""
                            INSERT INTO odds (league, home_team, away_team, bookmaker, 
                                            home_odds, away_odds, draw_odds, commence_time, timestamp)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (league_name, home_team, away_team, bookmaker_name,
                              home_odds, away_odds, draw_odds, commence_time))
                        
                        saved_count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return saved_count

def main():
    """Main collection loop"""
    print("🎯 Starting Odds Collector (Pinnacle only)...")
    
    while True:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting odds...")
        
        total_saved = 0
        
        for league_key, league_name in LEAGUES.items():
            odds_data = fetch_odds(league_key)
            saved = save_odds(odds_data, league_name)
            total_saved += saved
            print(f"✅ {league_name}: {saved} Pinnacle matches saved")
            time.sleep(1)  # Respect API rate limits
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collection complete! Total: {total_saved} matches")
        print("⏰ Collecting Pinnacle odds every 15 minutes. Press Ctrl+C to stop.")
        
        # Wait 15 minutes
        time.sleep(900)

if __name__ == "__main__":
    main()