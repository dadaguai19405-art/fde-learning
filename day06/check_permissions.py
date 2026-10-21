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
        cursor.execute("""
        SELECT current_user, rolsuper, rolcreaterole, rolcreatedb
        FROM pg_roles
        WHERE rolname = current_user
        """)
        print("当前角色权限：", cursor.fetchone())

        cursor.execute("""
        SELECT has_schema_privilege(current_user, 'public', 'CREATE')
        """)
        print("public schema CREATE 权限：", cursor.fetchone()[0])

        cursor.execute("""
        SELECT to_regclass('public.weather')
        """)
        print("weather 表：", cursor.fetchone()[0])
