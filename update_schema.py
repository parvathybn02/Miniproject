import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check and add columns to user table
columns_to_add = [
    ('last_login', 'DATETIME'),
    ('last_streak_update', 'DATETIME'),
    ('total_quizzes', 'INTEGER DEFAULT 0')
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name} to user table.")
    except sqlite3.OperationalError:
        print(f"Column {col_name} already exists in user table.")

conn.commit()
conn.close()
