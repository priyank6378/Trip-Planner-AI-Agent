import requests
import os

def get_weather_details(location, days=None):
    '''
    Fetches weather details for a given location and optional number of days.

    Parameters:
    - location (str): The location for which to fetch weather details.
    - days (int, optional): The number of days for the weather forecast. If not provided, current weather details will be fetched.
    '''
    key = os.getenv("WEATHER_API_KEY")
    url = "http://api.weatherapi.com/v1"
    forecast_endpoint = f"{url}/forecast.json"
    current_endpoint = f"{url}/current.json"

    parameters = {
        "key": key,
        "q": location,
    }

    if days:
        parameters["days"] = days
    

    response = requests.get(forecast_endpoint if days else current_endpoint, params=parameters)

    if response.status_code == 200:
        return str([{"type": "text", "text": str(response.json())}])
    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code} - {response.text}")
    

def get_tools_list():
    return {
        get_weather_details.__name__: get_weather_details.__doc__
    }


def get_tools_mapping():
    return {
        get_weather_details.__name__: get_weather_details
    }


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    location = "Pune"
    days = 2
    weather_details = get_weather_details(location, days)
    print(weather_details)