from day07.weather_advice import generate_advice


def test_hot_weather_advice():
    advice = generate_advice(33, 8, 30)

    assert "补水" in advice
    assert "升温" in advice


def test_cold_weather_advice():
    advice = generate_advice(2, 10, 5)

    assert "保暖" in advice
    assert "降温" in advice


def test_wind_advice():
    advice = generate_advice(25, 22, 25)

    assert "防风" in advice


def test_comfortable_advice():
    advice = generate_advice(24, 5)

    assert "舒适" in advice
