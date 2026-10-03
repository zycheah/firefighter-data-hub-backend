from datetime import date
from pydantic import BaseModel, Field


class LogEventDTO(BaseModel):
    event_date: date
    event_address: str = Field(..., min_length=1, max_length=255)
    is_same_ppe: bool


class LogEventResponseDTO(BaseModel):
    event_id: str
    access_token: str
    token_type: str = "bearer"