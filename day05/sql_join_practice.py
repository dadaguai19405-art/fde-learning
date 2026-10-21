import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "day04" / "weather.db"

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cities (
    name TEXT PRIMARY KEY,
    province TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
)
""")

cursor.executemany("""
INSERT OR IGNORE INTO cities (name, province, latitude, longitude)
VALUES (?, ?, ?, ?)
""", [
    ("上海", "上海市", 31.2304, 121.4737),
    ("北京", "北京市", 39.9042, 116.4074),
    ("深圳", "广东省", 22.5431, 114.0579),
    ("广州", "广东省", 23.1291, 113.2644),
])
conn.commit()


def show(title, sql):
    print(f"\n=== {title} ===")
    cursor.execute(sql)
    for row in cursor.fetchall():
        print(dict(row))


show("天气记录 + 城市信息", """
SELECT
    w.id,
    c.name,
    c.province,
    w.temperature,
    w.wind_speed,
    w.observed_at
FROM weather AS w
JOIN cities AS c
    ON w.city = c.name
ORDER BY w.id DESC
LIMIT 10
""")

show("每个城市的天气统计", """
SELECT
    c.name,
    c.province,
    COUNT(*) AS readings,
    ROUND(AVG(w.temperature), 1) AS avg_temp,
    MAX(w.temperature) AS max_temp,
    MIN(w.temperature) AS min_temp
FROM weather AS w
JOIN cities AS c
    ON w.city = c.name
GROUP BY c.name, c.province
HAVING COUNT(*) >= 4
ORDER BY avg_temp DESC
""")

show("所有城市（包括没有天气记录的城市）", """
SELECT
    c.name,
    c.province,
    COUNT(w.id) AS readings
FROM cities AS c
LEFT JOIN weather AS w
    ON w.city = c.name
GROUP BY c.name, c.province
ORDER BY readings DESC
""")

conn.close()
