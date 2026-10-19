import json

TASKS_FILE = "day02/tasks.json"

try:
    with open(TASKS_FILE, "r", encoding="utf-8") as file:
        tasks = json.load(file)
except FileNotFoundError:
    tasks = []


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)


while True:
    print("\n1. 添加任务")
    print("2. 查看任务")
    print("3. 退出")
    print("4. 完成任务")

    choice = input("请选择：")

    if choice == "1":
        title = input("任务内容：")
        tasks.append({"title": title, "done": False})
        save_tasks()
        print("已添加。")

    elif choice == "2":
        if len(tasks) == 0:
            print("还没有任务。")
        else:
            for index, task in enumerate(tasks, start=1):
                if task["done"]:
                    status = "已完成"
                else:
                    status = "未完成"
                print(f"{index}. {task['title']} - {status}")

    elif choice == "3":
        print("再见。")
        break

    elif choice == "4":
        number_text = input("要完成第几个任务？")
        try:
            number = int(number_text)
        except ValueError:
            print("请输入数字。")
            continue

        if 1 <= number <= len(tasks):
            tasks[number - 1]["done"] = True
            save_tasks()
            print("任务已完成。")
        else:
            print("没有这个任务编号。")

    else:
        print("请输入 1、2、3 或 4。")
