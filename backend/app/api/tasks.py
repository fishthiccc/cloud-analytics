import asyncio
import logging
from app.services.weather import fetch_temp
from app.services.metrics import create_weather_observation, get_or_create_town
from app.db.database import SessionLocal
from app.schemas.schemas import TownCreate, WeatherObservationCreate

logging.basicConfig(format='%(asctime)s - %(levelname) -8s %(message)s', level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

towns = ["Dublin", "Cork", "Galway", "Limerick", "Waterford"]

async def weather_update_once():
    logging.info("Starting one-off weather update...")
    db = SessionLocal()
    try:
        for town in towns:
            logging.info(f"Fetching weather data for {town}...")
            weather_data = await fetch_temp(town)
            print(f"Fetched weather data for {town}: {weather_data}")
            if weather_data:
                town_schema = TownCreate(
                    name=weather_data["name"],
                    latitude=weather_data["latitude"],
                    longitude=weather_data["longitude"],
                    region=weather_data.get("region")
                )
                town_obj = get_or_create_town(db, town_schema)

                town_name = town

                weather_observation_schema = WeatherObservationCreate(
                    town_name=town_name,
                    timestamp=weather_data["timestamp"],
                    temperature=weather_data["temperature"],
                    feels_like=weather_data.get("feels_like"),
                    humidity=weather_data.get("humidity"),
                    pressure=weather_data.get("pressure"),
                    wind_speed=weather_data.get("wind_speed"),
                    wind_direction=weather_data.get("wind_direction"),
                    cloud_coverage=weather_data.get("cloud_coverage"),
                    rainfall=weather_data.get("rainfall")
                )

                logging.info(f"Storing weather data for {town} in the database...")
                create_weather_observation(town_name, weather_observation_schema)
                logging.info(f"Weather data for {town} stored successfully.")
        logging.info("One-off weather update completed.")
    finally:
        db.close()


async def weather_update():
    while True:
        await weather_update_once()
        logging.info("Weather update task completed. Waiting for the next update...")
        await asyncio.sleep(3600)  # Wait for 1 hour before the next update