from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    original_filename: str
    s3_key: str
    content_type: str | None = None
    size_bytes: int | None = None
    download_url: str | None = None