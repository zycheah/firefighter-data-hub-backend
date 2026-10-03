from pydantic import BaseModel, EmailStr


class ResendVerificationDTO(BaseModel):
    email: EmailStr