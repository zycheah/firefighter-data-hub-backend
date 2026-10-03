from datetime import datetime
from pydantic import BaseModel


class LocationItem(BaseModel):
    latitude: float
    longitude: float
    accuracy_m: float | None = None
    recorded_at: datetime