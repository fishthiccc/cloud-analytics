from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.models.town import Town
from app.schemas import schemas
from app.models.weather_observation import WeatherObservation
from app.schemas.schemas import WeatherObservationCreate, TownCreate
from app.db.database import influx_client
from app.core.config import settings
from influxdb_client import Point


def get_or_create_town(db: Session, town_data: TownCreate) -> Town:
    town = db.query(Town).filter(Town.name == town_data.name).first()
    if town:
        town.latitude = town_data.latitude
        town.longitude = town_data.longitude
        town.region = town_data.region
        db.commit()
        db.refresh(town)
        return town

    new_town = Town(**town_data.dict())
    db.add(new_town)
    db.commit()
    db.refresh(new_town)
    return new_town

def create_weather_observation(town_name: str, observation: WeatherObservationCreate):
    try:
        point = Point("weather_observation") \
            .tag("town_name", town_name) \
            .field("temperature", observation.temperature) \
            .field("feels_like", observation.feels_like) \
            .field("humidity", observation.humidity) \
            .field("pressure", observation.pressure) \
            .field("wind_speed", observation.wind_speed) \
            .field("wind_direction", observation.wind_direction) \
            .field("cloud_coverage", observation.cloud_coverage) \
            .field("rainfall", observation.rainfall or 0) \
            .time(observation.timestamp)
        write_api = influx_client.write_api()
        write_api.write(bucket=settings.influxdb_bucket, org=settings.influxdb_org, record=point)
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")


# Town query functions
def get_towns(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(Town).offset(skip).limit(limit)
    return db.scalars(stmt).all()

def get_town(db: Session, town_id: int):
    stmt = select(Town).where(Town.id == town_id)
    return db.scalars(stmt).first()

def get_town_by_name(db: Session, town_name: str):
    stmt = select(Town).where(Town.name == town_name)
    return db.scalars(stmt).first()


# Weather observation query functions
def get_weather_observations(skip: int = 0, limit: int = 100):
    try:
        query = f'''

        from(bucket: "{settings.influxdb_bucket}")

          |> range(start: -30d)

          |> filter(fn: (r) => r._measurement == "weather_observation")

          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")

          |> sort(columns: ["_time"], desc: true)

          |> limit(n: {limit}, offset: {skip})

        '''

        query_api = influx_client.query_api()

        result = query_api.query(query=query, org=settings.influxdb_org)

        observations = []

        for table in result:

            for record in table.records:

                obs = {

                    'id': str(record.get_time()),

                    'town_name': record.values.get('town_name'),

                    'timestamp': record.get_time(),

                    'temperature': record.values.get('temperature'),

                    'feels_like': record.values.get('feels_like'),

                    'humidity': record.values.get('humidity'),

                    'pressure': record.values.get('pressure'),

                    'wind_speed': record.values.get('wind_speed'),

                    'wind_direction': record.values.get('wind_direction'),

                    'cloud_coverage': record.values.get('cloud_coverage'),

                    'rainfall': record.values.get('rainfall'),

                }

                observations.append(obs)

        return observations
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return []

def get_weather_observation(db: Session, observation_id: int):
    stmt = select(WeatherObservation).options(selectinload(WeatherObservation.town)).where(WeatherObservation.id == observation_id)
    obs = db.scalars(stmt).first()
    if obs:
        return {
            'id': obs.id,
            'temperature': obs.temperature,
            'feels_like': obs.feels_like,
            'humidity': obs.humidity,
            'pressure': obs.pressure,
            'wind_speed': obs.wind_speed,
            'wind_direction': obs.wind_direction,
            'cloud_coverage': obs.cloud_coverage,
            'rainfall': obs.rainfall,
            'town_name': obs.town.name if obs.town else None,
            'timestamp': obs.timestamp
        }
    return None

def get_weather_observations_by_town(db: Session, town_id: int, skip: int = 0, limit: int = 100):
    stmt = select(WeatherObservation).options(selectinload(WeatherObservation.town)).where(WeatherObservation.town_id == town_id).offset(skip).limit(limit)
    observations = db.scalars(stmt).all()
    result = []
    for obs in observations:
        obs_dict = {
            'id': obs.id,
            'temperature': obs.temperature,
            'feels_like': obs.feels_like,
            'humidity': obs.humidity,
            'pressure': obs.pressure,
            'wind_speed': obs.wind_speed,
            'wind_direction': obs.wind_direction,
            'cloud_coverage': obs.cloud_coverage,
            'rainfall': obs.rainfall,
            'town_name': obs.town.name if obs.town else None,
            'timestamp': obs.timestamp
        }
        result.append(obs_dict)
    return result

def get_latest_weather_observation(db: Session, town_id: int):
    stmt = select(WeatherObservation).options(selectinload(WeatherObservation.town)).where(WeatherObservation.town_id == town_id).order_by(WeatherObservation.timestamp.desc())
    obs = db.scalars(stmt).first()
    if obs:
        return {
            'id': obs.id,
            'temperature': obs.temperature,
            'feels_like': obs.feels_like,
            'humidity': obs.humidity,
            'pressure': obs.pressure,
            'wind_speed': obs.wind_speed,
            'wind_direction': obs.wind_direction,
            'cloud_coverage': obs.cloud_coverage,
            'rainfall': obs.rainfall,
            'town_name': obs.town.name if obs.town else None,
            'timestamp': obs.timestamp
        }
    return None