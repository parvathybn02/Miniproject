import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, summary, learning_path FROM study_material WHERE id = 4")
row = cursor.fetchone()
if row:
    print(f"ID 4 Summary: {row[1]}")
    print(f"ID 4 Path: {row[2]}")
else:
    print("ID 4 not found")

cursor.execute("SELECT count(*) FROM flashcard WHERE material_id = 4")
print(f"ID 4 Flashcards: {cursor.fetchone()[0]}")

cursor.execute("SELECT count(*) FROM quiz WHERE material_id = 4")
print(f"ID 4 Quizzes: {cursor.fetchone()[0]}")

conn.close()
