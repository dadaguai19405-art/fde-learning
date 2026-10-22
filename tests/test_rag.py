from day09.rag_answer import (
    answer_question,
    build_messages,
    build_query,
    parse_answer,
)
from day09.retriever import retrieve


def test_retrieve_heat_document():
    documents = retrieve("高温天气怎么补水 上海33°C")

    assert any(
        document["id"] == "heat"
        for document in documents
    )


def test_retrieve_wind_document():
    documents = retrieve("大风天骑车 风速22km/h")

    assert any(
        document["id"] == "wind"
        for document in documents
    )


def test_unknown_topic_has_no_documents():
    documents = retrieve("明天股票会涨吗")

    assert documents == []


def test_unknown_topic_refuses_without_llm():
    result = answer_question(
        "明天股票会涨吗？",
        "上海当前温度20°C，风速5km/h",
        api_config=None,
    )

    assert "无法判断" in result["answer"]
    assert result["citations"] == []
    assert result["retrieved"] == []


def test_build_query_includes_weather_context():
    query = build_query(
        "高温天气怎么补水",
        "上海当前温度33°C",
    )

    assert "上海" in query


def test_build_query_ignores_context_for_non_weather_question():
    query = build_query(
        "明天股票会涨吗",
        "上海当前温度20°C",
    )

    assert query == "明天股票会涨吗"


def test_build_messages_contains_sources():
    documents = retrieve("高温天气")
    messages = build_messages(
        "高温天气怎么补水",
        "上海33°C",
        documents,
    )

    assert "高温天气出行" in messages[1]["content"]
    assert "高温天气怎么补水" in messages[1]["content"]


def test_parse_answer_json():
    result = parse_answer(
        '{"answer": "多喝水", "citations": ["1"]}'
    )

    assert result == {"answer": "多喝水", "citations": ["1"]}


def test_parse_answer_fenced_json():
    result = parse_answer(
        '```json\n{"answer": "带外套", "citations": ["2"]}\n```'
    )

    assert result == {"answer": "带外套", "citations": ["2"]}


def test_parse_answer_malformed():
    result = parse_answer("不是 JSON")

    assert result["answer"] == "不是 JSON"
    assert result["citations"] == []


def test_heat_answer_without_llm():
    result = answer_question(
        "高温天气怎么补水？",
        "上海当前温度33°C，风速8km/h",
        api_config=None,
    )

    assert result["citations"] == ["1"]
    assert result["sources"][0]["id"] == "heat"


def test_answer_with_fake_llm_filters_invalid_citations(monkeypatch):
    monkeypatch.setattr(
        "day09.rag_answer.call_chat",
        lambda messages, api_config: (
            '{"answer": "注意补水和防晒", '
            '"citations": ["1", "99"]}'
        ),
    )

    result = answer_question(
        "高温天气怎么补水？",
        "上海当前温度33°C，风速8km/h",
        api_config={
            "api_key": "key",
            "base_url": "https://example.com/v1",
            "model": "model",
        },
    )

    assert result["answer"] == "注意补水和防晒"
    assert result["citations"] == ["1"]
