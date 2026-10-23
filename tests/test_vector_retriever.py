import math

import pytest

from day09.knowledge_base import DOCUMENTS
from day10.vector_retriever import (
    cosine_similarity,
    retrieve_vector,
    tokenize,
    vectorize,
)


def test_tokenize_chinese_text():
    tokens = tokenize("高温天气")

    assert "高温" in tokens
    assert "温天" in tokens
    assert "气" in tokens


def test_vectorize_is_normalized():
    vector = vectorize("高温天气")
    norm = math.sqrt(sum(value * value for value in vector))

    assert norm == pytest.approx(1.0)


def test_cosine_similarity_identical_vectors():
    vector = vectorize("大风天气")

    assert cosine_similarity(vector, vector) == pytest.approx(1.0)


def test_vector_retrieval_finds_heat_document():
    documents = retrieve_vector(
        "高温天气怎么补水",
        DOCUMENTS,
    )

    assert documents[0]["id"] == "heat"


def test_vector_retrieval_scores_are_sorted():
    documents = retrieve_vector(
        "大风天骑车",
        DOCUMENTS,
    )
    scores = [document["score"] for document in documents]

    assert scores == sorted(scores, reverse=True)
