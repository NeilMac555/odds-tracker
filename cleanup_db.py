import psycopg2

DATABASE_URL = 'postgresql://postgres:JkZHNPBGcZsgjLTKoFGlVhPHpVvxJEyS@caboose.proxy.rlwy.net:25023/railway'

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("DELETE FROM odds WHERE bookmaker != 'pinnacle';")
deleted_count = cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"✅ Deleted {deleted_count} non-Pinnacle odds!")