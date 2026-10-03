from pydantic import BaseModel, EmailStr


class UpdateMeRequestDTO(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    personal_email: EmailStr | None = None
    phoneNumber: str | None = None

