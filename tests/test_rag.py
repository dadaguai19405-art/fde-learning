from day09.rag_answer import answer_question
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
