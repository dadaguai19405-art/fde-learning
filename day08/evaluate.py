import time

from eval_cases import CASES
from llm_advice import generate_advice, load_config

api_config = load_config()
mode = "真实模型" if api_config else "模拟模型"
passed = 0
latencies = []

print(f"评测模式：{mode}")
print(f"用例数量：{len(CASES)}")
print()

for case in CASES:
    started = time.perf_counter()

    try:
        result = generate_advice(
            case["city"],
            case["temperature"],
            case["wind_speed"],
            case["previous_temperature"],
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

    advice = result["advice"]
    failures = []

    missing = [
        keyword
        for keyword in case["must_include"]
        if keyword not in advice
    ]
    if missing:
        failures.append(f"缺少关键词：{', '.join(missing)}")

    must_include_any = case.get("must_include_any", [])
    if must_include_any and not any(
        keyword in advice for keyword in must_include_any
    ):
        failures.append(
            f"缺少任一关键词：{', '.join(must_include_any)}"
        )

    if result["risk"] != case["expected_risk"]:
        failures.append(
            f"风险等级错误：期望 {case['expected_risk']}，"
            f"实际 {result['risk']}"
        )

    if len(advice) > case["max_length"]:
        failures.append(
            f"建议过长：{len(advice)} > {case['max_length']}"
        )

    forbidden_found = [
        keyword
        for keyword in case["forbidden"]
        if keyword in advice
    ]
    if forbidden_found:
        failures.append(
            f"出现禁止信息：{', '.join(forbidden_found)}"
        )

    ok = not failures

    if ok:
        passed += 1

    print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}")
    print(f"  建议：{advice}")
    print(f"  风险：{result['risk']}")
    print(f"  延迟：{elapsed:.2f}s")

    for failure in failures:
        print(f"  {failure}")

    print()

pass_rate = passed / len(CASES) * 100
avg_latency = sum(latencies) / len(latencies)

print(f"通过：{passed}/{len(CASES)}")
print(f"通过率：{pass_rate:.1f}%")
print(f"平均延迟：{avg_latency:.2f}s")
