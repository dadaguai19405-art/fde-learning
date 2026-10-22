import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day08.llm_advice import load_config
from day09.rag_answer import answer_question
from day09.rag_eval_cases import CASES

api_config = load_config()
mode = "真实模型" if api_config else "抽取式回退"
passed = 0
latencies = []

print(f"评测模式：{mode}")
print(f"用例数量：{len(CASES)}")
print()

for case in CASES:
    started = time.perf_counter()

    try:
        result = answer_question(
            case["question"],
            case["context"],
            api_config=api_config,
        )
    except Exception as error:
        elapsed = time.perf_counter() - started
        latencies.append(elapsed)
        print(f"[FAIL] {case['name']}")
        print(f"  API 错误：{error}")
        print(f"  延迟：{elapsed:.2f}s")
        print()
        continue

    elapsed = time.perf_counter() - started
    latencies.append(elapsed)

    answer = result["answer"]
    retrieved = result["retrieved"]
    retrieved_ids = [document["id"] for document in retrieved]
    citations = result["citations"]
    failures = []

    expected_sources = case["expected_sources"]

    if expected_sources and not any(
        source in retrieved_ids for source in expected_sources
    ):
        failures.append(
            f"检索未命中：期望 {expected_sources}，"
            f"实际 {retrieved_ids}"
        )

    if case.get("expected_empty_retrieval") and retrieved_ids:
        failures.append(f"应无检索结果，实际 {retrieved_ids}")

    if case["citation_required"] and not citations:
        failures.append("缺少引用编号")

    for citation in citations:
        if (
            not citation.isdigit()
            or not 1 <= int(citation) <= len(retrieved)
        ):
            failures.append(f"无效引用编号：{citation}")

    missing = [
        keyword
        for keyword in case["must_include"]
        if keyword not in answer
    ]
    if missing:
        failures.append(f"缺少关键词：{', '.join(missing)}")

    must_include_any = case["must_include_any"]
    if must_include_any and not any(
        keyword in answer for keyword in must_include_any
    ):
        failures.append(
            f"缺少任一关键词：{', '.join(must_include_any)}"
        )

    refusal_phrases = ["无法判断", "不能推断", "资料不足", "没有足够"]
    refused = any(phrase in answer for phrase in refusal_phrases)

    if case["expected_refusal"] and not refused:
        failures.append("应该拒答，但没有明确拒答")

    if not case["expected_refusal"] and refused:
        failures.append("不应拒答，但回答表示无法判断")

    forbidden_found = [
        keyword
        for keyword in case["forbidden"]
        if keyword in answer
    ]
    if forbidden_found:
        failures.append(
            f"出现禁止信息：{', '.join(forbidden_found)}"
        )

    if len(answer) > case["max_length"]:
        failures.append(
            f"回答过长：{len(answer)} > {case['max_length']}"
        )

    ok = not failures

    if ok:
        passed += 1

    print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}")
    print(f"  问题：{case['question']}")
    print(f"  回答：{answer}")
    print(f"  检索：{retrieved_ids}")
    print(f"  引用：{citations}")
    print(f"  延迟：{elapsed:.2f}s")

    for failure in failures:
        print(f"  {failure}")

    print()

pass_rate = passed / len(CASES) * 100
avg_latency = sum(latencies) / len(latencies)

print(f"通过：{passed}/{len(CASES)}")
print(f"通过率：{pass_rate:.1f}%")
print(f"平均延迟：{avg_latency:.2f}s")
