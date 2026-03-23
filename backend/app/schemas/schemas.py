from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TownBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    region: Optional[str] = None

class TownCreate(TownBase):
    pass

class TownOut(TownBase):
    id: int

    class Config:
        from_attributes = True

class WeatherObservationBase(BaseModel):
    temperature: float
    feels_like: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    cloud_coverage: Optional[int] = None
    rainfall: Optional[float] = None

class WeatherObservationCreate(WeatherObservationBase):
    town_name: str
    timestamp: datetime

class WeatherObservationOut(WeatherObservationBase):
    id: int
    town_name: str
    timestamp: datetime

    class Config:
        from_attributes = True