import asyncio
import logging
from app.services.weather import fetch_temp
from app.services.metrics import create_metric
from app.db.database import SessionLocal
from app.schemas.schemas import MetricCreate

logging.basicConfig(level=logging.INFO)

towns = ["Dublin", "Cork", "Galway", "Limerick", "Waterford"]

async def weather_update():
    while True:
        logging.info("Starting weather update task...")
        db = SessionLocal()
        for town in towns:
            logging.info(f"Fetching weather data for {town}...")
            metric_data = await fetch_temp(town)
            print(f"Fetched weather data for {town}: {metric_data}")  # Debugging line to check fetched data
            if metric_data:
                metric_schema = MetricCreate(**metric_data)
                logging.info(f"Storing weather data for {town} in the database...")
                create_metric(db, metric_schema)
                logging.info(f"Weather data for {town} stored successfully.")
        db.close()
        logging.info("Weather update task completed. Waiting for the next update...")

        await asyncio.sleep(3600)  # Wait for 1 hour before the next update