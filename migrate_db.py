import sqlite3
import os

db_path = os.path.join('instance', 'contacts.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('ALTER TABLE catalog_products ADD COLUMN in_stock BOOLEAN DEFAULT 1 NOT NULL;')
        conn.commit()
        print("Successfully added in_stock column to catalog_products.")
    except Exception as e:
        print("Error or already added:", e)
    finally:
        conn.close()
else:
    print(f"DB not found at {db_path}")
