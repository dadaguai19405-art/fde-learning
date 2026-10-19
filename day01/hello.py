# 第一天的小程序：自我介绍 + 年龄判断

name = input("你叫什么名字？")
if name == "":
    name = "朋友"
hobby = input("你的爱好是什么？")
while True:
    age_text = input("你多大了？")
    try:
        age = int(age_text)
        break
    except ValueError:
        print("请输入数字，例如 18。")

print(f"你好，{name}！你喜欢{hobby}。")

if age < 18:
    print("少年，先把基础打牢。")
elif age < 31:
    print("青年，正是学习的好时候。")
elif age < 61:
    print("中年，经验和执行力是你的优势。")
else:
    print("资深前辈，慢慢来。")
