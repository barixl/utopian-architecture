import sqlite3
import os

db_path = os.path.join('instance', 'contacts.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute('UPDATE catalog_products SET in_stock = 0 WHERE id = 1')
    conn.commit()
    print("Updated id 1 to out of stock.")
except Exception as e:
    print(e)
finally:
    conn.close()
