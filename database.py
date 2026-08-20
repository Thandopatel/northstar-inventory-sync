import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "inventory.db")

def get_db_connection():
    """Get database connection and ensure table exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_cache (
            sku TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn