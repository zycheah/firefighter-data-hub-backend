from pydantic import BaseModel

class PasswordResetDTO(BaseModel):
    password: str
    newPassword: str