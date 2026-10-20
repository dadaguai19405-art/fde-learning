import sqlite3
from datetime import datetime
from pathlib import Path

import requests

DB_FILE = Path(__file__).with_name("weather.db")
API_URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 31.2304,
    "longitude": 121.4737,
    "current": "temperature_2m,wind_speed_10m",
    "timezone": "Asia/Shanghai",
}

response = requests.get(API_URL, params=params, timeout=30)
response.raise_for_status()
data = response.json()
current = data["current"]

temperature = current["temperature_2m"]
wind_speed = current["wind_speed_10m"]
observed_at = current["time"]
fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    temperature REAL NOT NULL,
    wind_speed REAL NOT NULL,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL
)
""")

cursor.execute(
    """
    INSERT INTO weather
        (city, temperature, wind_speed, observed_at, fetched_at)
    VALUES
        (?, ?, ?, ?, ?)
    """,
    ("上海", temperature, wind_speed, observed_at, fetched_at),
)
conn.commit()

print(f"上海当前温度：{temperature}°C")
print(f"风速：{wind_speed} km/h")
print(f"观测时间：{observed_at}")

cursor.execute("""
SELECT id, city, temperature, wind_speed, observed_at
FROM weather
ORDER BY id DESC
LIMIT 5
""")

print("\n最近 5 条记录：")
for row in cursor.fetchall():
    print(row)

conn.close()
