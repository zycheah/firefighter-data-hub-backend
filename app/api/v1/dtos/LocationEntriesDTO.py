from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class LocationEntryDTO(BaseModel):
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    locationTimestamp: Optional[datetime] = None
    accuracy: Optional[float] = None
    altitude: Optional[float] = None

    class Config:
        # Import for SQL alchemy
        from_attributes = True