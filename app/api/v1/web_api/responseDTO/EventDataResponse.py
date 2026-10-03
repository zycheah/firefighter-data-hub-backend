from datetime import datetime
from pydantic import BaseModel
import uuid


class EventData(BaseModel):
    event_id: uuid.UUID
    user_id: uuid.UUID
    event_date: datetime
    event_address: str
    is_same_ppe: bool


class EventDataResponse(BaseModel):
    results: list[EventData] = []
    count: int = 0

