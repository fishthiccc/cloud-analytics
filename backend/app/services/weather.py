import os
import httpx
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

async def fetch_temp(town: str) -> dict | None:
    """
    Fetch current temperature for a town in Ireland from OpenWeatherMap.
    """
    params = {
          "q": f"{town},IE",
          "appid": API_KEY,
          "units": "metric" 
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
               
            return {
                "timestamp": datetime.utcfromtimestamp(data["dt"]),
                "name": town.upper(),
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "region": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "cloud_coverage": data["clouds"]["all"],
                "rainfall": 0
            }
     
        except httpx.RequestError as e:
            print(f"Error fetching weather data for {town}: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {town}: {e}")
        return None