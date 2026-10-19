def check_password(password):
    if len(password) < 10:
        return False, "密码太短，至少 10 位。"

    has_digit = False
    for char in password:
        if char.isdigit():
            has_digit = True

    if not has_digit:
        return False, "密码里至少要有一个数字。"

    return True, "密码合格。"


def run_password_check():
    for attempt in range(5):
        password = input("请输入密码：")
        ok, message = check_password(password)
        print(message)

        if ok:
            return True

    print("5 次机会用完了，账号暂时锁定。")
    return False


run_password_check()