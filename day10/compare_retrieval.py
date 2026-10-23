import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day09.knowledge_base import DOCUMENTS
from day09.rag_answer import build_query
from day09.rag_eval_cases import CASES
from day09.retriever import retrieve
from day10.vector_retriever import retrieve_vector


def hit(documents, expected_sources):
    document_ids = [document["id"] for document in documents]

    if not expected_sources:
        return len(document_ids) == 0

    return any(
        source in document_ids
        for source in expected_sources
    )


keyword_hits = 0
vector_hits = 0

print(f"对比用例：{len(CASES)}")
print()

for case in CASES:
    query = build_query(case["question"], case["context"])
    expected = case["expected_sources"]

    keyword_docs = retrieve(query, top_k=2)
    vector_docs = retrieve_vector(query, DOCUMENTS, top_k=2)

    keyword_ok = hit(keyword_docs, expected)
    vector_ok = hit(vector_docs, expected)

    if keyword_ok:
        keyword_hits += 1

    if vector_ok:
        vector_hits += 1

    print(f"问题：{case['question']}")
    print(
        "  期望：",
        expected or "无检索结果",
    )
    print(
        "  关键词：",
        [document["id"] for document in keyword_docs],
        "PASS" if keyword_ok else "FAIL",
    )
    print(
        "  向量：",
        [
            (document["id"], round(document["score"], 4))
            for document in vector_docs
        ],
        "PASS" if vector_ok else "FAIL",
    )
    print()

total = len(CASES)

print(f"关键词命中：{keyword_hits}/{total}")
print(f"向量命中：{vector_hits}/{total}")
