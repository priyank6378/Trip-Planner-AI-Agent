from mcp.server import FastMCP
import os
import requests
import json

import dotenv
dotenv.load_dotenv()

mcp = FastMCP("Trip Planner MCP", json_response=True)

@mcp.tool()
def get_weather_details(location: str, days: int | None = None) -> dict:
    '''
    Fetches weather details for a given location and optional number of days.

    Parameters:
    - location (str): The location for which to fetch weather details.
    - days (int, optional): The number of days for the weather forecast. If not provided, current weather details will be fetched.
    '''
    key = os.getenv("WEATHER_API_KEY")
    url = "http://api.weatherapi.com/v1"
    forecast_endpoint = f"{url}/forecast.json"

    parameters = {
        "key": key,
        "q": location,
        "days": days or 1
    }

    response = requests.get(forecast_endpoint , params=parameters)

    if response.status_code == 200:
        return json.dumps({"result": response.json()})
        # return json.dumps({"result": "26° C, Partly cloudy"})
    else:
        return json.dumps({"error": f"Failed to fetch weather data: {response.status_code}"})
    

@mcp.tool()
def save_my_trip_plan(trip_plan: str) -> str:
    '''
    Saves the trip plan details to a file.

    Parameters:
    - trip_plan (str): The trip plan details to be saved.
    '''
    with open("trip_plan.md", "w") as file:
        file.write(trip_plan)
    
    return "Trip plan saved successfully!"


if __name__ == "__main__":
    mcp.run(transport="stdio")