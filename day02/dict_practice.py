person = {
    "name": "小明",
    "age": 20
}

print(person["name"])
print(person["age"])

person["city"] = "上海"
person["age"] = 21
person["hobby"] = "篮球"

for key, value in person.items():
    print(key, value)

print(person["hobby"])
