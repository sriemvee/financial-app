import sqlite3
from db.schema import SCHEMA_SQL, SEED_SQL

conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Execute schema
cursor.executescript(SCHEMA_SQL)

# Execute seed data
cursor.executescript(SEED_SQL)

conn.commit()
conn.close()

print("✅ Database initialized successfully!")
