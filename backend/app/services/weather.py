import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(API_KEY)  # Debugging line to check if the API key is loaded correctly
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

async def fetch_temp(town: str) -> dict | None:
    """
    Fetch current temperature for a town in Ireland from OpenWeatherMap.
    Returns a dictionary compatible with MetricCreate schema.
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
                "name": town.upper(),
                "value": data["main"]["temp"]
            }
     
        except httpx.RequestError as e:
            print(f"Error fetching weather data for {town}: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {town}: {e}")
        return None