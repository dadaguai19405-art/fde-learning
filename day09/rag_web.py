import sys
from pathlib import Path

import psycopg
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day09.rag_answer import answer_question

DATABASE_URL = st.secrets["postgres"]["url"]

CITIES = {
    "上海": {"latitude": 31.2304, "longitude": 121.4737},
    "北京": {"latitude": 39.9042, "longitude": 116.4074},
    "深圳": {"latitude": 22.5431, "longitude": 114.0579},
}


def load_llm_config():
    try:
        llm = st.secrets["llm"]
    except (KeyError, FileNotFoundError):
        return None

    try:
        return {
            "api_key": llm["api_key"],
            "base_url": llm["base_url"],
            "model": llm["model"],
        }
    except KeyError:
        return None


def query_db(sql, params=()):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                return cursor.fetchall()
            return []


LLM_CONFIG = load_llm_config()

st.set_page_config(page_title="天气知识助手", page_icon="📚")
st.title("天气知识助手")
st.caption("RAG：先检索资料，再生成带引用的回答")

city = st.selectbox("选择城市", list(CITIES.keys()))

latest = query_db("""
SELECT temperature, wind_speed, observed_at
FROM weather
WHERE city = %s
ORDER BY id DESC
LIMIT 1
""", (city,))

if latest:
    temperature, wind_speed, observed_at = latest[0]
    weather_context = (
        f"{city} 当前温度 {temperature}°C，风速 {wind_speed} km/h"
    )
    st.caption(f"当前数据：{weather_context}")
else:
    weather_context = ""
    st.warning("这个城市还没有天气记录，请先在天气页面获取一次。")

question = st.text_input(
    "问一个问题",
    placeholder="例如：高温天气怎么补水？",
)

if st.button("检索并回答", type="primary"):
    if not question.strip():
        st.warning("请先输入问题。")
    elif not latest:
        st.warning("没有当前天气数据，暂时无法回答。")
    else:
        with st.spinner("正在检索资料并生成回答..."):
            try:
                result = answer_question(
                    question.strip(),
                    weather_context,
                    api_config=LLM_CONFIG,
                )
            except Exception as error:
                st.error("回答失败，请稍后重试。")
                with st.expander("查看错误详情"):
                    st.code(str(error))
            else:
                st.subheader("回答")
                st.write(result["answer"])

                if result["sources"]:
                    st.subheader("参考资料")
                    for source in result["sources"]:
                        st.markdown(f"**{source['title']}**")
                        st.write(source["content"])

                citations = ", ".join(result["citations"]) or "无"
                st.caption(f"引用编号：{citations}")

st.divider()
st.caption(
    "可以问：高温补水、低温保暖、大风骑行、户外运动、"
    "降雨雷电、空气质量。"
)
