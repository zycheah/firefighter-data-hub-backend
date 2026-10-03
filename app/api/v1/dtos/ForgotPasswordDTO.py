from pydantic import BaseModel, EmailStr


class ForgotPasswordRequestDTO(BaseModel):
    email: EmailStr


class ForgotPasswordConfirmDTO(BaseModel):
    email: EmailStr
    newPassword: str