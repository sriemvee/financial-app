import sqlite3
import os

# Read schema.sql and seed.sql files directly
with open('db/schema.sql', 'r') as f:
    schema = f.read()

with open('db/seed.sql', 'r') as f:
    seed = f.read()

conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

cursor.executescript(schema)
cursor.executescript(seed)

conn.commit()
conn.close()

print("✅ Database initialized!")
