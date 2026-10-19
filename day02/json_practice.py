import json

tasks = [
    {"title": "学 Python", "done": False},
    {"title": "跑步", "done": True}
]

with open("day02/test_tasks.json", "w", encoding="utf-8") as file:
    json.dump(tasks, file, ensure_ascii=False, indent=2)

print("已保存到 day02/test_tasks.json")

with open("day02/test_tasks.json", "r", encoding="utf-8") as file:
    loaded_tasks = json.load(file)

print(loaded_tasks)
