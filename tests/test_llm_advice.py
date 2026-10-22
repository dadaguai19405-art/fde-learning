from day08.llm_advice import mock_llm, parse_response


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
