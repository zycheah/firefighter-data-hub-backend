from pydantic import BaseModel
from typing import Optional


class PpeDTO(BaseModel):
    event_id: Optional[str] = None
    helmet_id: str = ""
    hood_id: str = ""
    face_mask_id: str = ""
    scba_id: str = ""
    glove_id: str = ""
    boot_id: str = ""
    bunker_coat_id: str = ""
    bunker_pants_id: str = ""
    is_ppe_updated: bool = False


class PpeResponseDTO(BaseModel):
    ppe_id: str
    access_token: str
    token_type: str = "bearer"