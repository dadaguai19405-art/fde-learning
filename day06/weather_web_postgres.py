from datetime import datetime

import pandas as pd
import psycopg
import requests
import streamlit as st

DATABASE_URL = st.secrets["postgres"]["url"]
API_URL = "https://api.open-meteo.com/v1/forecast"

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


query_db("""
CREATE TABLE IF NOT EXISTS weather (
    id BIGSERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    wind_speed DOUBLE PRECISION NOT NULL,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL
)
""")

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
LIMIT 1
""", (city,))

if latest:
    temperature, wind_speed, observed_at = latest[0]
    col1, col2 = st.columns(2)
    col1.metric(f"{city}温度", f"{temperature} °C")
    col2.metric("风速", f"{wind_speed} km/h")
    st.caption(f"观测时间：{observed_at}")

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
