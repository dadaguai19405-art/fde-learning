import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg
import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day08.llm_advice import generate_advice

DATABASE_URL = st.secrets["postgres"]["url"]
API_URL = "https://api.open-meteo.com/v1/forecast"


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


LLM_CONFIG = load_llm_config()

CITIES = {
    "上海": {"latitude": 31.2304, "longitude": 121.4737},
    "北京": {"latitude": 39.9042, "longitude": 116.4074},
    "深圳": {"latitude": 22.5431, "longitude": 114.0579},
}


def query_db(sql, params=()):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                return cursor.fetchall()
            return []


def fetch_weather(city):
    params = {
        "latitude": CITIES[city]["latitude"],
        "longitude": CITIES[city]["longitude"],
        "current": "temperature_2m,wind_speed_10m",
        "timezone": "Asia/Shanghai",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    current = response.json()["current"]
    return (
        current["temperature_2m"],
        current["wind_speed_10m"],
        current["time"],
    )


# weather 表由数据库管理员一次性创建，应用只负责读写。

st.set_page_config(page_title="城市天气 · Postgres", page_icon="🌤️")
st.title("城市天气")
st.caption("数据存储：Supabase Postgres")

city = st.selectbox("选择城市", list(CITIES.keys()))

if st.button(f"获取{city}最新天气", type="primary"):
    try:
        temperature, wind_speed, observed_at = fetch_weather(city)
        fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query_db(
            """
            INSERT INTO weather
                (city, temperature, wind_speed, observed_at, fetched_at)
            VALUES
                (%s, %s, %s, %s, %s)
            """,
            (city, temperature, wind_speed, observed_at, fetched_at),
        )

        st.success("已获取并保存到 Supabase。")
        st.rerun()

    except requests.RequestException as error:
        st.error(f"获取天气失败：{error}")

latest = query_db("""
SELECT temperature, wind_speed, observed_at
FROM weather
WHERE city = %s
ORDER BY id DESC
LIMIT 2
""", (city,))

if latest:
    temperature, wind_speed, observed_at = latest[0]
    previous_temperature = (
        latest[1][0] if len(latest) > 1 else None
    )

    col1, col2 = st.columns(2)
    col1.metric(f"{city}温度", f"{temperature} °C")
    col2.metric("风速", f"{wind_speed} km/h")
    st.caption(f"观测时间：{observed_at}")

    st.subheader("出行建议")

    if "advice_cache" not in st.session_state:
        st.session_state.advice_cache = {}

    advice_key = (
        city,
        observed_at,
        temperature,
        wind_speed,
        previous_temperature,
    )

    if LLM_CONFIG:
        st.caption(f"建议模型：{LLM_CONFIG['model']}")
    else:
        st.caption("建议模型：规则模式（未配置 [llm]）")

    if st.button("生成 AI 出行建议", type="secondary"):
        with st.spinner("正在生成建议..."):
            try:
                result = generate_advice(
                    city,
                    temperature,
                    wind_speed,
                    previous_temperature,
                    api_config=LLM_CONFIG,
                )
                mode = (
                    f"真实模型：{LLM_CONFIG['model']}"
                    if LLM_CONFIG
                    else "规则模式"
                )
            except Exception as error:
                result = generate_advice(
                    city,
                    temperature,
                    wind_speed,
                    previous_temperature,
                    api_config=None,
                )
                mode = "规则回退"
                st.warning("模型调用失败，已回退到规则建议。")
                with st.expander("查看错误详情"):
                    st.code(str(error))

        st.session_state.advice_cache[advice_key] = {
            "result": result,
            "mode": mode,
        }

    cached_advice = st.session_state.advice_cache.get(advice_key)

    if cached_advice:
        result = cached_advice["result"]
        st.info(result["advice"])
        st.caption(
            f"建议来源：{cached_advice['mode']} · "
            f"风险等级：{result['risk']}"
        )
    else:
        st.caption("点击上面的按钮生成出行建议，避免每次刷新都调用模型。")

st.subheader(f"{city}最近记录")

rows = query_db("""
SELECT id, city, temperature, wind_speed, observed_at, fetched_at
FROM weather
WHERE city = %s
ORDER BY id DESC
LIMIT 20
""", (city,))

if rows:
    df = pd.DataFrame(
        rows,
        columns=["ID", "城市", "温度(°C)", "风速(km/h)", "观测时间", "抓取时间"]
    )
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("这个城市还没有记录，点击上面的按钮获取一次。")

st.subheader("温度趋势")

history = query_db("""
SELECT observed_at, temperature
FROM weather
WHERE city = %s
ORDER BY id DESC
LIMIT 50
""", (city,))

if history:
    history = list(reversed(history))
    history_df = pd.DataFrame(history, columns=["观测时间", "温度(°C)"])
    st.line_chart(history_df, x="观测时间", y="温度(°C)")
else:
    st.info("还没有足够的数据画趋势图。")
