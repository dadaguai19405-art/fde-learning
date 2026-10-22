from eval_cases import CASES
from llm_advice import generate_advice, load_config


api_config = load_config()
mode = "真实模型" if api_config else "模拟模型"
passed = 0

print(f"评测模式：{mode}")
print(f"用例数量：{len(CASES)}")
print()

for case in CASES:
    try:
        result = generate_advice(
            case["city"],
            case["temperature"],
            case["wind_speed"],
            case["previous_temperature"],
            api_config=api_config,
        )
    except Exception as error:
        print(f"[FAIL] {case['name']}")
        print(f"  API 错误：{error}")
        print()
        continue

    advice = result["advice"]
    missing = [
        keyword
        for keyword in case["must_include"]
        if keyword not in advice
    ]
    ok = not missing

    if ok:
        passed += 1

    print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}")
    print(f"  建议：{advice}")
    print(f"  风险：{result['risk']}")

    if missing:
        print(f"  缺少关键词：{', '.join(missing)}")

    print()

pass_rate = passed / len(CASES) * 100
print(f"通过：{passed}/{len(CASES)}")
print(f"通过率：{pass_rate:.1f}%")
