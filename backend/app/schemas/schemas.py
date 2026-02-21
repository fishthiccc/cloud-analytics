from pydantic import BaseModel
from datetime import datetime

class MetricCreate(BaseModel):
    name: str
    value: float

class MetricOut(BaseModel):
    id: int
    name: str
    value: float
    created_at: datetime

    class Config:
        orm_mode = True