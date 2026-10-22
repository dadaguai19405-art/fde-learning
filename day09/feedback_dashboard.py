import sys
from pathlib import Path

import pandas as pd
import psycopg
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_URL = st.secrets["postgres"]["url"]


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
                created_at
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
                "created_at",
            ]

    return pd.DataFrame(rows, columns=columns)


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
    st.error("读取反馈失败，请检查数据库连接和 RLS 策略。")
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

col1, col2, col3, col4 = st.columns(4)
col1.metric("总反馈", total)
col2.metric("有帮助", up_count)
col3.metric("没帮助", down_count)
col4.metric("好评率", f"{positive_rate:.1f}%")

st.subheader("筛选")

filter_col1, filter_col2, filter_col3 = st.columns(3)

rating_options = ["全部", "up", "down"]
rating = filter_col1.selectbox("评价", rating_options)

city_options = ["全部"] + sorted(feedback["city"].unique().tolist())
city = filter_col2.selectbox("城市", city_options)

model_options = ["全部"] + sorted(feedback["model"].unique().tolist())
model = filter_col3.selectbox("模型", model_options)

filtered = feedback.copy()

if rating != "全部":
    filtered = filtered[filtered["rating"] == rating]

if city != "全部":
    filtered = filtered[filtered["city"] == city]

if model != "全部":
    filtered = filtered[filtered["model"] == model]

st.subheader("反馈记录")
st.dataframe(
    filtered,
    width="stretch",
    hide_index=True,
)

csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "下载当前筛选结果 CSV",
    data=csv_data,
    file_name="rag_feedback.csv",
    mime="text/csv",
)

st.subheader("差评分析")

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
        title = f"{row['city']} · {row['question']} · {row['failure_type']}"

        with st.expander(title):
            st.markdown("**回答**")
            st.write(row["answer"])
            st.markdown("**引用编号**")
            st.write(row["citations"] or "无")
            st.markdown("**模型**")
            st.write(row["model"])
            st.markdown("**时间**")
            st.write(row["created_at"])
