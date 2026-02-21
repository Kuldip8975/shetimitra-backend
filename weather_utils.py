import requests

API_KEY = "91e936bb9d1ae2b2671d1399359afbd6"

def is_rain_expected(city):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    data = requests.get(url).json()

    # next 6 hours check
    for item in data.get("list", [])[:2]:
        if "rain" in item:
            return True
    return False
