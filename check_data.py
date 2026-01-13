import psycopg2

DATABASE_URL = 'postgresql://postgres:JkZHNPBGcZsgjLTKoFGlVhPHpVvxJEyS@caboose.proxy.rlwy.net:25023/railway'

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("Running query...")
cur.execute("""
    SELECT league, home_team, away_team, timestamp, commence_time 
    FROM odds 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

rows = cur.fetchall()
print(f"Found {len(rows)} rows")

if rows:
    print("\nRecent matches across all leagues:")
    for row in rows:
        print(f"{row[0]}: {row[1]} vs {row[2]}")
        print(f"  Collection time: {row[3]}")
        print(f"  Match date: {row[4]}")
        print()
else:
    print("No matches found!")

conn.close()
print("Done!")