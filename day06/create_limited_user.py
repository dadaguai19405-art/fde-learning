import re
import secrets
import string
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from psycopg import sql

SECRETS_FILE = (
    Path(__file__).resolve().parent.parent
    / ".streamlit"
    / "secrets.toml"
)
ROLE_NAME = "weather_app"

with open(SECRETS_FILE, "rb") as file:
    config = tomllib.load(file)

admin_url = config["postgres"]["url"]
parsed = urlparse(admin_url)
project_ref = parsed.username.split(".", 1)[1]

alphabet = string.ascii_letters + string.digits
password = "".join(secrets.choice(alphabet) for _ in range(24))

with psycopg.connect(admin_url) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (ROLE_NAME,),
        )
        role_exists = cursor.fetchone() is not None

        if role_exists:
            cursor.execute(
                sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {}").format(
                    sql.Identifier(ROLE_NAME),
                    sql.Literal(password),
                )
            )
        else:
            cursor.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(ROLE_NAME),
                    sql.Literal(password),
                )
            )

        cursor.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(parsed.path.lstrip("/")),
                sql.Identifier(ROLE_NAME),
            )
        )
        cursor.execute(
            sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                sql.Identifier(ROLE_NAME)
            )
        )
        cursor.execute(
            sql.SQL(
                "GRANT SELECT, INSERT, UPDATE ON TABLE public.weather TO {}"
            ).format(sql.Identifier(ROLE_NAME))
        )

        cursor.execute(
            "SELECT pg_get_serial_sequence('public.weather', 'id')"
        )
        sequence_name = cursor.fetchone()[0]
        cursor.execute(
            sql.SQL("GRANT USAGE, SELECT ON SEQUENCE {} TO {}").format(
                sql.SQL(sequence_name),
                sql.Identifier(ROLE_NAME),
            )
        )

new_username = f"{ROLE_NAME}.{project_ref}"
new_netloc = (
    f"{new_username}:{password}@{parsed.hostname}:{parsed.port or 5432}"
)
new_url = parsed._replace(netloc=new_netloc).geturl()

text = SECRETS_FILE.read_text(encoding="utf-8")
new_text, count = re.subn(
    r'(?m)^url\s*=\s*".*"$',
    f'url = "{new_url}"',
    text,
)

if count != 1:
    print("无法自动更新 secrets.toml，请手动更新。")
    raise SystemExit(1)

SECRETS_FILE.write_text(new_text, encoding="utf-8")

print("受限用户 weather_app 已创建或更新。")
print("连接用户名格式：", new_username)
print("新密码已自动生成，并写入 .streamlit/secrets.toml。")
print("请把本地 secrets.toml 的内容复制到 Streamlit Cloud Secrets。")
