import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day08.llm_advice import load_config
from day09.rag_answer import answer_question

api_config = load_config()
weather_context = "上海当前温度 33°C，风速 8 km/h"

questions = [
    "高温天气怎么补水？",
    "零下温度怎么穿？",
    "大风天骑车要注意什么？",
    "今天会下雨吗？",
]

for question in questions:
    result = answer_question(
        question,
        weather_context,
        api_config=api_config,
    )

    print(f"问题：{question}")
    print(f"回答：{result['answer']}")
    print(f"引用：{result['citations']}")
    print(
        "来源：",
        ", ".join(source["title"] for source in result["sources"]),
    )
    print()
