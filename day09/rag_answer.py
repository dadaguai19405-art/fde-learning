import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from day08.llm_advice import call_chat
from day09.retriever import retrieve

RAG_SYSTEM_PROMPT = """
你是天气知识助手。只能依据提供的资料回答，不得编造资料中没有的事实。

规则：
1. 如果资料不足，明确回答“根据现有资料无法判断”；
2. 当前天气数据只有温度和风速，不要推断降雨、空气质量或未来预报；
3. 回答要简洁、可执行；
4. 引用资料编号，只输出 JSON。

JSON 格式：
{"answer": "回答内容", "citations": ["1", "2"]}
""".strip()


def build_query(question, weather_context):
    return f"{question} {weather_context}"


def build_messages(question, weather_context, documents):
    blocks = []

    for index, document in enumerate(documents, start=1):
        blocks.append(
            f"[{index}] {document['title']}\n"
            f"{document['content']}"
        )

    evidence = "\n\n".join(blocks)

    user_prompt = (
        f"可用资料：\n{evidence}\n\n"
        f"当前天气数据：{weather_context}\n"
        f"用户问题：{question}"
    )

    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_answer(text):
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
        answer = str(data.get("answer", "")).strip()
        citations = data.get("citations", [])

        if isinstance(citations, str):
            citations = [citations]

        citations = [str(item) for item in citations]

        if answer:
            return {"answer": answer, "citations": citations}
    except json.JSONDecodeError:
        pass

    return {
        "answer": cleaned,
        "citations": [],
        "raw": text,
    }


def answer_question(question, weather_context, api_config=None):
    query = build_query(question, weather_context)
    documents = retrieve(query, top_k=2)

    if not documents:
        return {
            "answer": "根据现有资料无法判断。",
            "citations": [],
            "sources": [],
        }

    if api_config is None:
        return {
            "answer": documents[0]["content"],
            "citations": ["1"],
            "sources": documents[:1],
        }

    messages = build_messages(question, weather_context, documents)
    content = call_chat(messages, api_config)
    parsed = parse_answer(content)

    valid_numbers = {
        str(index)
        for index in range(1, len(documents) + 1)
    }
    citations = [
        number
        for number in parsed["citations"]
        if number in valid_numbers
    ]

    sources = [
        documents[int(number) - 1]
        for number in citations
    ]

    return {
        "answer": parsed["answer"],
        "citations": citations,
        "sources": sources,
    }
