import tomllib
from pathlib import Path

import psycopg

SECRETS_FILE = (
    Path(__file__).resolve().parent.parent
    / ".streamlit"
    / "secrets.toml"
)

if not SECRETS_FILE.exists():
    print(f"找不到配置文件：{SECRETS_FILE}")
    print("请先创建 .streamlit/secrets.toml，并填入 Supabase 连接串。")
    raise SystemExit(1)

with open(SECRETS_FILE, "rb") as file:
    secrets = tomllib.load(file)

database_url = secrets["postgres"]["url"]

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user, version()"
        )
        database, user, version = cursor.fetchone()

print("连接成功")
print("数据库：", database)
print("用户：", user)
print("版本：", version.split(",")[0])
