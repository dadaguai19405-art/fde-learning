import pytest

from day08.llm_advice import (
    build_user_prompt,
    call_chat,
    call_llm,
    generate_advice,
    load_config_from_env,
    mock_llm,
    parse_response,
)


def test_mock_high_risk():
    result = mock_llm("北京", 38, 5, 36)

    assert result["risk"] == "高"
    assert "补水" in result["advice"]


def test_mock_medium_risk():
    result = mock_llm("北京", 2, 10, 5)

    assert result["risk"] == "中"


def test_parse_json_response():
    result = parse_response(
        '{"advice": "建议带外套", "risk": "中"}'
    )

    assert result == {
        "advice": "建议带外套",
        "risk": "中",
    }


def test_parse_malformed_response():
    result = parse_response("不是 JSON")

    assert result["advice"] == "不是 JSON"
    assert result["risk"] == "未知"


def test_parse_fenced_json_response():
    result = parse_response(
        '```json\n{"advice": "带伞", "risk": "低"}\n```'
    )

    assert result == {"advice": "带伞", "risk": "低"}


def test_build_user_prompt_with_previous_temperature():
    prompt = build_user_prompt("上海", 22, 5, 20)

    assert "上海" in prompt
    assert "+2.0°C" in prompt


def test_build_user_prompt_without_history():
    prompt = build_user_prompt("上海", 22, 5, None)

    assert "没有上一条记录" in prompt


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "model")

    config = load_config_from_env()

    assert config == {
        "api_key": "key",
        "base_url": "https://example.com/v1",
        "model": "model",
    }


def test_load_config_without_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    assert load_config_from_env() is None


def test_load_config_requires_base_url(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("LLM_MODEL", "model")

    with pytest.raises(ValueError):
        load_config_from_env()


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"advice": "注意补水", "risk": "中"}'
                        )
                    }
                }
            ]
        }


def test_call_chat(monkeypatch):
    monkeypatch.setattr(
        "day08.llm_advice.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = call_chat(
        [{"role": "user", "content": "你好"}],
        {
            "api_key": "key",
            "base_url": "https://example.com/v1",
            "model": "model",
        },
    )

    assert "补水" in result


def test_call_llm(monkeypatch):
    monkeypatch.setattr(
        "day08.llm_advice.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = call_llm(
        "上海",
        33,
        8,
        30,
        {
            "api_key": "key",
            "base_url": "https://example.com/v1",
            "model": "model",
        },
    )

    assert result == {"advice": "注意补水", "risk": "中"}


def test_generate_advice_with_mock_config(monkeypatch):
    monkeypatch.setattr(
        "day08.llm_advice.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = generate_advice(
        "上海",
        33,
        8,
        30,
        api_config={
            "api_key": "key",
            "base_url": "https://example.com/v1",
            "model": "model",
        },
    )

    assert result["risk"] == "中"
