from pydantic import BaseModel


class VerifyEmailDTO(BaseModel):
    token: str