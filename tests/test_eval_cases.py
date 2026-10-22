from day08.eval_cases import CASES as ADVICE_CASES
from day09.rag_eval_cases import CASES as RAG_CASES


def test_advice_cases_are_complete():
    for case in ADVICE_CASES:
        assert case["name"]
        assert case["expected_risk"] in {"低", "中", "高"}
        assert "must_include" in case
        assert "max_length" in case


def test_rag_cases_are_complete():
    for case in RAG_CASES:
        assert case["name"]
        assert case["question"]
        assert case["context"]
        assert "expected_sources" in case
        assert "expected_refusal" in case
        assert "citation_required" in case


def test_rag_case_names_are_unique():
    names = [case["name"] for case in RAG_CASES]

    assert len(names) == len(set(names))
