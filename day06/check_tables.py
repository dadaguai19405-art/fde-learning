import tomllib
from pathlib import Path

import psycopg

SECRETS_FILE = (
    Path(__file__).resolve().parent.parent
    / ".streamlit"
    / "secrets.toml"
)

with open(SECRETS_FILE, "rb") as file:
    secrets = tomllib.load(file)

database_url = secrets["postgres"]["url"]

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        print("当前数据库和用户：", cursor.fetchone())

        cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """)

        tables = cursor.fetchall()

        if tables:
            print("public schema 中的表：")
            for schema, table in tables:
                print(f"- {schema}.{table}")
        else:
            print("public schema 中没有表")
