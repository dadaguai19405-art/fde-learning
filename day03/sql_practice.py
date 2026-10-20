import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).with_name("tasks.db")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
)
""")

cursor.execute("SELECT COUNT(*) FROM tasks")
if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [("学 SQL", 0), ("跑步", 0)]
    )
    conn.commit()

cursor.execute("UPDATE tasks SET done = 0")
conn.commit()


def show_tasks():
    cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
    for row in cursor.fetchall():
        print(row)


print("全部任务：")
show_tasks()

cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (1,))
conn.commit()

print("\n更新后：")
show_tasks()

conn.close()
