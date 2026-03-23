from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import (
    TownOut, TownCreate,
    WeatherObservationOut, WeatherObservationCreate
)
from app.services.metrics import (
    get_towns,
    get_town,
    get_town_by_name,
    get_weather_observations,
    get_weather_observation,
    get_weather_observations_by_town,
    get_latest_weather_observation
)
from app.api.tasks import weather_update_once
from app.db.deps import get_db

# Towns router
towns_router = APIRouter(
    prefix="/api/v1/towns",
    tags=["towns"]
)

# Weather observations router
weather_router = APIRouter(
    prefix="/api/v1/weather",
    tags=["weather"]
)

# Towns endpoints
@towns_router.get("/", response_model=list[TownOut])
def read_towns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_towns(db, skip, limit)

@towns_router.get("/{town_id}", response_model=TownOut)
def read_town(
    town_id: int,
    db: Session = Depends(get_db)
):
    town = get_town(db, town_id)
    if town is None:
        raise HTTPException(status_code=404, detail="Town not found")
    return town

@towns_router.get("/by-name/{town_name}", response_model=TownOut)
def read_town_by_name(
    town_name: str,
    db: Session = Depends(get_db)
):
    town = get_town_by_name(db, town_name.upper())
    if town is None:
        raise HTTPException(status_code=404, detail="Town not found")
    return town

@towns_router.delete("/{town_id}")
def delete_town(
    town_id: int,
    db: Session = Depends(get_db)
):
    town = get_town(db, town_id)
    if town is None:
        raise HTTPException(status_code=404, detail="Town not found")
    db.delete(town)
    db.commit()
    return {"detail": "Town deleted successfully"}  


# Weather observation endpoints
@weather_router.get("/", response_model=list[WeatherObservationOut])
def read_weather_observations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_weather_observations(skip, limit)

@weather_router.get("/{observation_id}", response_model=WeatherObservationOut)
def read_weather_observation(
    observation_id: int,
    db: Session = Depends(get_db)
):
    observation = get_weather_observation(db, observation_id)
    if observation is None:
        raise HTTPException(status_code=404, detail="Weather observation not found")
    return observation

@weather_router.get("/town/{town_id}", response_model=list[WeatherObservationOut])
def read_weather_observations_by_town(
    town_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_weather_observations_by_town(db, town_id, skip, limit)

@weather_router.get("/town/{town_id}/latest", response_model=WeatherObservationOut)
def read_latest_weather_observation(
    town_id: int,
    db: Session = Depends(get_db)
):
    observation = get_latest_weather_observation(db, town_id)
    if observation is None:
        raise HTTPException(status_code=404, detail="No weather observations found for this town")
    return observation


@weather_router.post("/refresh")
async def trigger_weather_refresh():
    await weather_update_once()
    return {"status": "ok", "message": "Weather refresh triggered"}


