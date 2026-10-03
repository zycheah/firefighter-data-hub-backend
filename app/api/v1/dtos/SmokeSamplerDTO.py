from pydantic import BaseModel, Field


class SmokeSampleDTO(BaseModel):
    chemical_name: str = Field(..., min_length=1, max_length=255)
    percentage_proportion: float = Field(..., ge=0, le=100)


class SmokeSamplerSubmitDTO(BaseModel):
    samples: list[SmokeSampleDTO] = Field(..., min_length=1, max_length=50)


class SmokeSamplerSubmitResponseDTO(BaseModel):
    submission_id: str
    access_token: str
    token_type: str = "bearer"