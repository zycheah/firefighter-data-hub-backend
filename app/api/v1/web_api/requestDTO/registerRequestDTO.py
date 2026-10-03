from pydantic import BaseModel, EmailStr

class RegisterRequestDTO(BaseModel):
    first_name: str
    last_name: str
    university_email: EmailStr
    personal_email: EmailStr | None = None
    phoneNumber: str | None = None
    role: str
    password: str