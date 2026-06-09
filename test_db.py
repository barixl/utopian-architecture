import sqlite3
import os

db_path = os.path.join('instance', 'contacts.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute('SELECT id, name, in_stock FROM catalog_products')
    rows = cur.fetchall()
    for row in rows:
        print(row)
except Exception as e:
    print(e)
finally:
    conn.close()
