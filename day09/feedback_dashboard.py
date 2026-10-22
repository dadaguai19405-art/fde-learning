import sys
from pathlib import Path

import pandas as pd
import psycopg
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_URL = st.secrets["postgres"]["url"]

STATUS_LABELS = {
    "open": "待处理",
    "resolved": "已修复",
    "ignored": "忽略",
}
STATUS_VALUES = {
    label: value
    for value, label in STATUS_LABELS.items()
}


def query_feedback():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT
                id,
                city,
                question,
                answer,
                citations,
                model,
                rating,
                status,
                note,
                created_at,
                updated_at
            FROM rag_feedback
            ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            columns = [
                "id",
                "city",
                "question",
                "answer",
                "citations",
                "model",
                "rating",
                "status",
                "note",
                "created_at",
                "updated_at",
            ]

    return pd.DataFrame(rows, columns=columns)


def update_feedback(feedback_id, status, note):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE rag_feedback
            SET
                status = %s,
                note = %s,
                updated_at = NOW()
            WHERE id = %s
            """, (status, note, feedback_id))


def classify_failure(row):
    answer = row["answer"]

    if not row["citations"]:
        return "无引用/检索失败"

    if "无法判断" in answer or "资料不足" in answer:
        return "拒答或资料不足"

    if "当前" in answer and "不适用" in answer:
        return "当前上下文冲突"

    return "待人工分类"


st.set_page_config(page_title="RAG 反馈看板", page_icon="📊")
st.title("RAG 反馈看板")
st.caption("数据来源：Supabase public.rag_feedback")

try:
    feedback = query_feedback()
except Exception as error:
    st.error(
        "读取反馈失败。请确认已经执行 feedback_setup.sql "
        "和 feedback_status_setup.sql。"
    )
    with st.expander("查看错误详情"):
        st.code(str(error))
    st.stop()

if feedback.empty:
    st.info("还没有反馈数据，先在 RAG 页面提交几条评价。")
    st.stop()

total = len(feedback)
up_count = int((feedback["rating"] == "up").sum())
down_count = int((feedback["rating"] == "down").sum())
positive_rate = up_count / total * 100
pending_down = int(
    (
        (feedback["rating"] == "down")
        & (feedback["status"] == "open")
    ).sum()
)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("总反馈", total)
col2.metric("有帮助", up_count)
col3.metric("没帮助", down_count)
col4.metric("好评率", f"{positive_rate:.1f}%")
col5.metric("待处理差评", pending_down)

st.subheader("筛选")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

rating = filter_col1.selectbox(
    "评价",
    ["全部", "up", "down"],
)

city_options = ["全部"] + sorted(feedback["city"].unique().tolist())
city = filter_col2.selectbox("城市", city_options)

model_options = ["全部"] + sorted(feedback["model"].unique().tolist())
model = filter_col3.selectbox("模型", model_options)

status_options = ["全部"] + list(STATUS_LABELS.values())
status_label = filter_col4.selectbox("处理状态", status_options)

filtered = feedback.copy()

if rating != "全部":
    filtered = filtered[filtered["rating"] == rating]

if city != "全部":
    filtered = filtered[filtered["city"] == city]

if model != "全部":
    filtered = filtered[filtered["model"] == model]

if status_label != "全部":
    filtered = filtered[
        filtered["status"] == STATUS_VALUES[status_label]
    ]

display = filtered.copy()
display["status"] = display["status"].map(STATUS_LABELS)

st.subheader("反馈记录")
st.dataframe(
    display,
    width="stretch",
    hide_index=True,
)

csv_data = display.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "下载当前筛选结果 CSV",
    data=csv_data,
    file_name="rag_feedback.csv",
    mime="text/csv",
)

st.subheader("差评处理")

down_feedback = feedback[feedback["rating"] == "down"].copy()

if down_feedback.empty:
    st.success("当前没有差评。")
else:
    down_feedback["failure_type"] = down_feedback.apply(
        classify_failure,
        axis=1,
    )

    type_counts = (
        down_feedback["failure_type"]
        .value_counts()
        .rename_axis("失败类型")
        .reset_index(name="数量")
    )
    st.dataframe(type_counts, width="stretch", hide_index=True)

    for _, row in down_feedback.iterrows():
        current_status = (
            row["status"]
            if row["status"] in STATUS_LABELS
            else "open"
        )
        current_label = STATUS_LABELS[current_status]
        title = (
            f"{row['city']} · {row['question']} · "
            f"{row['failure_type']} · {current_label}"
        )

        with st.expander(title):
            st.markdown("**回答**")
            st.write(row["answer"])
            st.markdown("**引用编号**")
            st.write(row["citations"] or "无")
            st.markdown("**模型**")
            st.write(row["model"])
            st.markdown("**创建时间**")
            st.write(row["created_at"])
            st.markdown("**最后更新**")
            st.write(row["updated_at"])

            with st.form(f"feedback_form_{row['id']}"):
                labels = list(STATUS_LABELS.values())
                selected_status = st.selectbox(
                    "处理状态",
                    labels,
                    index=labels.index(current_label),
                    key=f"status_{row['id']}",
                )
                note = st.text_area(
                    "处理备注",
                    value=row["note"] or "",
                    key=f"note_{row['id']}",
                    placeholder="例如：已加入回归测试 / 属于资料缺失 / 暂不处理",
                )
                saved = st.form_submit_button("保存处理结果")

            if saved:
                update_feedback(
                    int(row["id"]),
                    STATUS_VALUES[selected_status],
                    note.strip(),
                )
                st.success("处理结果已保存。")
                st.rerun()
