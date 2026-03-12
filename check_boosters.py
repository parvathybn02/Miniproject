import sqlite3
import os

db_path = os.path.join('instance', 'study_platform.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT material_id, revision_notes, probable_questions FROM exam_booster")
rows = cursor.fetchall()

print("Exam Boosters:")
for row in rows:
    notes_len = len(row[1]) if row[1] else 0
    questions_count = len(row[2]) if row[2] else 0
    print(f"Material ID: {row[0]}, Notes Len: {notes_len}, Questions JSON Len: {questions_count}")

conn.close()
