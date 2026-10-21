def generate_advice(temperature, wind_speed, previous_temperature=None):
    if temperature >= 30:
        advice = "天气炎热，建议穿轻薄衣物，注意补水和防晒。"
    elif temperature >= 20:
        advice = "温度舒适，适合正常出行。"
    elif temperature >= 10:
        advice = "天气偏凉，建议加一件外套。"
    else:
        advice = "天气寒冷，注意保暖。"

    if wind_speed >= 20:
        advice += " 风速较大，外出注意防风。"
    elif wind_speed >= 12:
        advice += " 风有点大，骑行时注意安全。"

    if previous_temperature is not None:
        change = temperature - previous_temperature

        if change >= 2:
            advice += f" 比上次升温 {change:.1f}°C。"
        elif change <= -2:
            advice += f" 比上次降温 {abs(change):.1f}°C。"
        else:
            advice += " 温度变化不大。"

    return advice


if __name__ == "__main__":
    print(generate_advice(32, 10, 30))
    print(generate_advice(18, 25, 22))
    print(generate_advice(25, 5, 25))
