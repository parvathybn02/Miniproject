import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, filename, length(content_text) FROM study_material")
rows = cursor.fetchall()

print("All Materials:")
for row in rows:
    print(f"ID: {row[0]}, File: {row[1]}, Text Length: {row[2]}")

conn.close()
