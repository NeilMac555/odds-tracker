import requests
import sqlite3
from datetime import datetime
import time
import schedule

import os
API_KEY = os.getenv('ODDS_API_KEY', 'bc5c2e6fce5dc1683f0267a02e8afe05')

LEAGUES = {
    "EPL": "soccer_epl",
    "La Liga": "soccer_spain_la_liga",
    "Bundesliga": "soccer_germany_bundesliga",
    "Serie A": "soccer_italy_serie_a",
    "Ligue 1": "soccer_france_ligue_one"
}

# Create database
def init_db():
    conn = sqlite3.connect('odds_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            league TEXT,
            match_id TEXT,
            home_team TEXT,
            away_team TEXT,
            bookmaker TEXT,
            market TEXT,
            outcome_name TEXT,
            price REAL,
            point REAL
        )
    ''')
    conn.commit()
    conn.close()

def collect_odds():
    print(f"[{datetime.now()}] Collecting odds...")
    
    conn = sqlite3.connect('odds_tracker.db')
    c = conn.cursor()
    
    for league_name, sport_key in LEAGUES.items():
        url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'
        params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'h2h,spreads,totals', 'oddsFormat': 'decimal'}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            matches = response.json()
            timestamp = datetime.now().isoformat()
            
            for match in matches:
                match_id = match['id']
                home = match['home_team']
                away = match['away_team']
                
                for bookmaker in match.get('bookmakers', []):
                    if bookmaker['key'] in ['pinnacle', 'betfair_ex_eu']:
                        bookie_name = bookmaker['title']
                        
                        for market in bookmaker['markets']:
                            market_key = market['key']
                            
                            for outcome in market['outcomes']:
                                c.execute('''
                                    INSERT INTO odds_history 
                                    (timestamp, league, match_id, home_team, away_team, bookmaker, market, outcome_name, price, point)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    timestamp, league_name, match_id, home, away,
                                    bookie_name, market_key, outcome['name'],
                                    outcome['price'], outcome.get('point', 0)
                                ))
            
            print(f"✅ {league_name}: {len(matches)} matches saved")
    
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Collection complete!\n")

if __name__ == "__main__":
    print("🚀 Starting Odds Collector...")
    init_db()
    
    # Collect immediately on start
    collect_odds()
    
    # Then every 15 minutes
    schedule.every(15).minutes.do(collect_odds)
    
    print("📊 Collecting odds every 15 minutes. Press Ctrl+C to stop.\n")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
        