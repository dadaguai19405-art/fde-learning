import sqlite3
from contextlib import closing
from pathlib import Path

import streamlit as st

DB_FILE = Path(__file__).with_name("tasks.db")


def query_db(sql, params=()):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            cursor = conn.execute(sql, params)
            return cursor.fetchall()


query_db("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
)
""")

st.set_page_config(page_title="FDE 任务清单", page_icon="✅")
st.title("FDE 任务清单")
st.caption("网页和命令行共用同一个 SQLite 数据库")

with st.form("add_task_form", clear_on_submit=True):
    title = st.text_input("新任务", placeholder="例如：学完 SQL 查询")
    submitted = st.form_submit_button("添加任务")

if submitted:
    if title.strip():
        query_db(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (title.strip(),)
        )
        st.rerun()
    else:
        st.warning("任务内容不能为空。")

rows = query_db("SELECT id, title, done FROM tasks ORDER BY id")

st.subheader("任务列表")

if not rows:
    st.info("还没有任务，先添加一个吧。")
else:
    for task_id, task_title, done in rows:
        col1, col2 = st.columns([5, 1])

        with col1:
            checked = st.checkbox(
                task_title,
                value=bool(done),
                key=f"task_{task_id}"
            )

        with col2:
            st.write("✅" if done else "⏳")

        if checked != bool(done):
            query_db(
                "UPDATE tasks SET done = ? WHERE id = ?",
                (1 if checked else 0, task_id)
            )
            st.rerun()

done_count = sum(1 for _, _, done in rows if done)

st.divider()
st.caption(f"共 {len(rows)} 个任务，已完成 {done_count} 个。")
