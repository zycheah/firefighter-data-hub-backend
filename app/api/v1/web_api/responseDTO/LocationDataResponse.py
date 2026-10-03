from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

import uuid

class LocationData(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    locationTimestamp: Optional[datetime] = None
    accuracy: Optional[float] = None
    altitude: Optional[float] = None

class LocationDataResponse(BaseModel):
    results: list[LocationData]=[]
    count: int = 0