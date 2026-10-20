import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

DB_FILE = Path(__file__).with_name("weather.db")
API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 31.2304,
    "longitude": 121.4737,
    "current": "temperature_2m,wind_speed_10m",
    "timezone": "Asia/Shanghai",
}


def query_db(sql, params=()):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            cursor = conn.execute(sql, params)
            return cursor.fetchall()


def fetch_weather():
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    current = response.json()["current"]
    return (
        current["temperature_2m"],
        current["wind_speed_10m"],
        current["time"],
    )


query_db("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    temperature REAL NOT NULL,
    wind_speed REAL NOT NULL,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL
)
""")

st.set_page_config(page_title="上海天气", page_icon="🌤️")
st.title("上海天气")
st.caption("数据来源：Open-Meteo")

if st.button("获取最新天气", type="primary"):
    try:
        temperature, wind_speed, observed_at = fetch_weather()
        fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query_db(
            """
            INSERT INTO weather
                (city, temperature, wind_speed, observed_at, fetched_at)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            ("上海", temperature, wind_speed, observed_at, fetched_at),
        )

        st.success("已获取并保存最新天气。")
        st.rerun()

    except requests.RequestException as error:
        st.error(f"获取天气失败：{error}")

latest = query_db("""
SELECT temperature, wind_speed, observed_at
FROM weather
ORDER BY id DESC
LIMIT 1
""")

if latest:
    temperature, wind_speed, observed_at = latest[0]
    col1, col2 = st.columns(2)
    col1.metric("当前温度", f"{temperature} °C")
    col2.metric("风速", f"{wind_speed} km/h")
    st.caption(f"观测时间：{observed_at}")

st.subheader("最近记录")

rows = query_db("""
SELECT id, city, temperature, wind_speed, observed_at, fetched_at
FROM weather
ORDER BY id DESC
LIMIT 20
""")

if rows:
    df = pd.DataFrame(
        rows,
        columns=["ID", "城市", "温度(°C)", "风速(km/h)", "观测时间", "抓取时间"]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("还没有记录，点击上面的按钮获取一次。")
