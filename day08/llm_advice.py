import json
import os
import tomllib
from pathlib import Path

import requests

SYSTEM_PROMPT = """
你是天气出行助手。根据用户提供的城市、温度、风速和温度变化，
用中文给出不超过 80 字的出行建议。

要求：
1. 必须给出穿衣或出行建议；
2. 风速大于等于 20 km/h 时，明确提醒防风；
3. 温度变化达到 2°C 时，明确说明升温或降温；
4. 只输出 JSON，不要输出 Markdown 或额外解释。

JSON 格式：
{"advice": "建议文字", "risk": "低|中|高"}
""".strip()


def build_user_prompt(
    city,
    temperature,
    wind_speed,
    previous_temperature,
):
    if previous_temperature is None:
        trend = "没有上一条记录"
    else:
        change = temperature - previous_temperature
        trend = f"比上次变化 {change:+.1f}°C"

    return (
        f"城市：{city}\n"
        f"当前温度：{temperature}°C\n"
        f"风速：{wind_speed} km/h\n"
        f"趋势：{trend}"
    )


def mock_llm(
    city,
    temperature,
    wind_speed,
    previous_temperature,
):
    if temperature >= 30:
        advice = f"{city}天气炎热，穿轻薄衣物，注意补水和防晒。"
        risk = "中"
    elif temperature >= 20:
        advice = f"{city}温度舒适，适合正常出行。"
        risk = "低"
    elif temperature >= 10:
        advice = f"{city}天气偏凉，建议加一件外套。"
        risk = "低"
    else:
        advice = f"{city}天气寒冷，注意保暖。"
        risk = "中"

    if wind_speed >= 20:
        advice += " 风速较大，注意防风。"
        risk = "高"

    if previous_temperature is not None:
        change = temperature - previous_temperature
        if change >= 2:
            advice += f" 比上次升温 {change:.1f}°C。"
        elif change <= -2:
            advice += f" 比上次降温 {abs(change):.1f}°C。"

    return {"advice": advice, "risk": risk}


def parse_response(text):
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
        advice = str(data.get("advice", "")).strip()
        risk = str(data.get("risk", "未知")).strip()

        if advice:
            return {"advice": advice, "risk": risk}
    except json.JSONDecodeError:
        pass

    return {
        "advice": cleaned,
        "risk": "未知",
        "raw": text,
    }


def load_config_from_env():
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    if not api_key:
        return None

    if not base_url or not model:
        raise ValueError(
            "设置了 LLM_API_KEY，但缺少 LLM_BASE_URL 或 LLM_MODEL。"
        )

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def load_config_from_secrets_file():
    secrets_file = (
        Path(__file__).resolve().parent.parent
        / ".streamlit"
        / "secrets.toml"
    )

    if not secrets_file.exists():
        return None

    with open(secrets_file, "rb") as file:
        config = tomllib.load(file)

    llm = config.get("llm")

    if not llm:
        return None

    api_key = llm.get("api_key")
    base_url = llm.get("base_url")
    model = llm.get("model")

    if not api_key:
        return None

    if not base_url or not model:
        raise ValueError(
            "secrets.toml 的 [llm] 缺少 base_url 或 model。"
        )

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def load_config():
    return load_config_from_env() or load_config_from_secrets_file()


def call_llm(
    city,
    temperature,
    wind_speed,
    previous_temperature,
    api_config,
):
    prompt = build_user_prompt(
        city,
        temperature,
        wind_speed,
        previous_temperature,
    )

    response = requests.post(
        f"{api_config['base_url'].rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": api_config["model"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return parse_response(content)


def generate_advice(
    city,
    temperature,
    wind_speed,
    previous_temperature,
    api_config=None,
):
    if api_config is None:
        return mock_llm(
            city,
            temperature,
            wind_speed,
            previous_temperature,
        )

    return call_llm(
        city,
        temperature,
        wind_speed,
        previous_temperature,
        api_config,
    )
