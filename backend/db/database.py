import sqlite3
import os
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/expenses.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            cursor.executescript(f.read())
    conn.commit()
    conn.close()

def seed_db():
    seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
    if os.path.exists(seed_path):
        conn = get_db_connection()
        cursor = conn.cursor()
        with open(seed_path, 'r') as f:
            cursor.executescript(f.read())
        conn.commit()
        conn.close()

def execute_query(query: str, params: tuple = () ):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def execute_update(query: str, params: tuple = () ):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def close_db(conn):
    if conn:
        conn.close()