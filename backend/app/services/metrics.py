from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.models.town import Town
from app.schemas import schemas
from app.models.weather_observation import WeatherObservation
from app.schemas.schemas import WeatherObservationCreate, TownCreate
from app.db.database import influx_client
from app.core.config import settings
from influxdb_client import Point
import threading

# Global counter for observation IDs in InfluxDB
_observation_id_counter = 0  # Start from 1 for new observations (migration assigned 1-76)
_counter_lock = threading.Lock()

def _get_next_observation_id():
    """Get next sequential ID for weather observations"""
    global _observation_id_counter
    with _counter_lock:
        _observation_id_counter += 1
        return _observation_id_counter

def _reassign_chronological_ids():
    """Reassign all observation_ids based on chronological order"""
    try:
        # Query all observations sorted by timestamp
        query = f'''
        from(bucket: "{settings.influxdb_bucket}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "weather_observation")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: false)
        '''
        
        query_api = influx_client.query_api()
        result = query_api.query(query=query, org=settings.influxdb_org)
        
        # Collect all observations with their timestamps
        observations = []
        for table in result:
            for record in table.records:
                obs = {
                    '_time': record.get_time(),
                    'town_name': record.values.get('town_name'),
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
        
        if not observations:
            return
        
        # Sort by timestamp (already sorted, but ensure)
        observations.sort(key=lambda x: x['_time'])
        
        # Delete all existing observations
        delete_api = influx_client.delete_api()
        delete_api.delete(
            start="2026-03-20T00:00:00Z",
            stop="2030-01-01T00:00:00Z",
            predicate='_measurement=="weather_observation"',
            bucket=settings.influxdb_bucket,
            org=settings.influxdb_org
        )
        
        # Reinsert with chronological IDs
        write_api = influx_client.write_api()
        for i, obs in enumerate(observations, 1):
            point = Point("weather_observation") \
                .tag("town_name", obs['town_name']) \
                .field("observation_id", i) \
                .field("temperature", obs['temperature']) \
                .field("feels_like", obs['feels_like']) \
                .field("humidity", obs['humidity']) \
                .field("pressure", obs['pressure']) \
                .field("wind_speed", obs['wind_speed']) \
                .field("wind_direction", obs['wind_direction']) \
                .field("cloud_coverage", obs['cloud_coverage']) \
                .field("rainfall", obs['rainfall']) \
                .time(obs['_time'])
            
            write_api.write(bucket=settings.influxdb_bucket, org=settings.influxdb_org, record=point)
        
        # Update counter
        global _observation_id_counter
        _observation_id_counter = len(observations)
        
        print(f"Reassigned chronological IDs to {len(observations)} observations")
        
    except Exception as e:
        print(f"Error reassigning chronological IDs: {e}")
        import traceback
        traceback.print_exc()


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

          |> sort(columns: ["_time"])

          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")

          |> limit(n: {limit}, offset: {skip})

        '''

        query_api = influx_client.query_api()

        result = query_api.query(query=query, org=settings.influxdb_org)

        observations = []

        for table in result:
            for record in table.records:
                obs = {
                    'id': 0,  # Will assign after sorting
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

        # Sort by timestamp in Python
        observations.sort(key=lambda x: x['timestamp'])
        
        # Assign sequential IDs based on chronological order
        for i, obs in enumerate(observations, 1 + skip):
            obs['id'] = i

        return observations
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        import traceback
        traceback.print_exc()
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