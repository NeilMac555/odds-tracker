import psycopg2
import os

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

# Create database connection
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS odds (
    id SERIAL PRIMARY KEY,
    league TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    bookmaker TEXT NOT NULL,
    home_odds REAL NOT NULL,
    away_odds REAL NOT NULL,
    draw_odds REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create index for faster queries
cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_odds_timestamp ON odds(timestamp DESC)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_odds_match ON odds(league, home_team, away_team)
''')

conn.commit()
cursor.close()
conn.close()

print("✅ PostgreSQL database initialized successfully")
