from pydantic import BaseModel


class DeleteAccountDTO(BaseModel):
    password: str