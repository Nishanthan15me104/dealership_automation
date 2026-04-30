import sqlite3
import pandas as pd

DB_PATH = "dealerships.db"

def init_db():
    """Initializes the database using the SQL dump."""
    conn = sqlite3.connect(DB_PATH)
    with open('database.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def get_brands():
    """Returns a list of brand tuples (id, name)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM brands")
    brands = cursor.fetchall()
    conn.close()
    return brands

def get_dealerships(brand_id):
    """Returns dealerships for a specific brand."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, panel_image_path, logo_image_path FROM dealerships WHERE brand_id = ?", (brand_id,))
    dealers = cursor.fetchall()
    conn.close()
    return dealers