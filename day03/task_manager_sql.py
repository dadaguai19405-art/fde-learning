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
conn.commit()

while True:
    print("\n1. 添加任务")
    print("2. 查看任务")
    print("3. 退出")
    print("4. 完成任务")

    choice = input("请选择：")

    if choice == "1":
        title = input("任务内容：")
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (title,)
        )
        conn.commit()
        print("已添加。")

    elif choice == "2":
        cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cursor.fetchall()

        if len(rows) == 0:
            print("还没有任务。")
        else:
            for task_id, title, done in rows:
                status = "已完成" if done == 1 else "未完成"
                print(f"{task_id}. {title} - {status}")

    elif choice == "3":
        print("再见。")
        break

    elif choice == "4":
        number_text = input("要完成第几个任务？")

        try:
            task_id = int(number_text)
        except ValueError:
            print("请输入数字。")
            continue

        cursor.execute(
            "UPDATE tasks SET done = 1 WHERE id = ?",
            (task_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            print("没有这个任务编号。")
        else:
            print("任务已完成。")

    else:
        print("请输入 1、2、3 或 4。")

conn.close()
