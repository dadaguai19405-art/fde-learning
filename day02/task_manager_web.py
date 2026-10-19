import json
from pathlib import Path

import streamlit as st

TASKS_FILE = Path(__file__).with_name("tasks.json")


def load_tasks():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)


st.set_page_config(page_title="FDE 任务清单", page_icon="✅")
st.title("FDE 任务清单")
st.caption("用浏览器管理你的学习任务")

tasks = load_tasks()

with st.form("add_task_form", clear_on_submit=True):
    title = st.text_input("新任务", placeholder="例如：学完 Python 列表")
    submitted = st.form_submit_button("添加任务")

if submitted:
    if title.strip():
        tasks.append({"title": title.strip(), "done": False})
        save_tasks(tasks)
        st.rerun()
    else:
        st.warning("任务内容不能为空。")

st.subheader("任务列表")

if not tasks:
    st.info("还没有任务，先添加一个吧。")
else:
    for index, task in enumerate(tasks):
        col1, col2 = st.columns([5, 1])

        with col1:
            checked = st.checkbox(
                task["title"],
                value=task["done"],
                key=f"task_{index}"
            )

        with col2:
            st.write("✅" if task["done"] else "⏳")

        if checked != task["done"]:
            tasks[index]["done"] = checked
            save_tasks(tasks)
            st.rerun()

done_count = sum(1 for task in tasks if task["done"])

st.divider()
st.caption(f"共 {len(tasks)} 个任务，已完成 {done_count} 个。")
