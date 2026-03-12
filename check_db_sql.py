import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, filename, summary FROM study_material ORDER BY id DESC")
    rows = cursor.fetchall()
    print(f"Materials: {len(rows)}")
    for row in rows:
        summary_len = len(row[2]) if row[2] else 0
        print(f"ID: {row[0]}, File: {row[1]}, Summary Len: {summary_len}")
        if row[2]:
            print(f"  Summary start: {row[2][:50]}...")
except Exception as e:
    print(f"Error: {e}")

conn.close()
