from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegisterDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str
    email: EmailStr
    password: str
    role: str = "firefighter"
    phoneNumber: Optional[str] = None

    gender: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    year_of_birth: Optional[int] = None

    height_cm: float
    weight_kg: float

    dominant_hand: str
    # Accept both historical payload keys:
    # - `Years_of_experience` (legacy, incorrect casing)
    # - `years_of_experience` (preferred)
    years_of_experience: str = Field(..., alias="Years_of_experience")

    firefighter_status: str
    type_of_firefighter: str
    firefighter_station_name: str

    city: str
    state: str
