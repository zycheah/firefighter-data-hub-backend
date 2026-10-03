from pydantic import BaseModel


class PasswordResetRequestDTO(BaseModel):
    password: str
    newPassword: str

