import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, filename FROM study_material WHERE filename LIKE '%.pdf'")
rows = cursor.fetchall()
print("PDF Materials:")
for row in rows:
    print(f"ID: {row[0]}, File: {row[1]}")
conn.close()
