from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_db, get_current_user
from app.models.uploaded_file import UploadedFile
from app.models.userModel import UserModel
from app.core.s3 import get_s3_client, build_s3_key
from app.core.config import settings

router = APIRouter()


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    s3 = get_s3_client()
    file_bytes = file.file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    s3_key = build_s3_key(current_user.id, file.filename)

    s3.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes,
        ContentType=file.content_type or "application/octet-stream",
    )

    row = UploadedFile(
        user_id=current_user.id,
        original_filename=file.filename,
        s3_key=s3_key,
        content_type=file.content_type,
        size_bytes=len(file_bytes),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "original_filename": row.original_filename,
        "s3_key": row.s3_key,
        "content_type": row.content_type,
        "size_bytes": row.size_bytes,
    }


@router.get("")
def list_files(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    s3 = get_s3_client()
    rows = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.created_at.desc())
        .all()
    )

    result = []
    for row in rows:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": row.s3_key},
            ExpiresIn=3600,
        )
        result.append(
            {
                "id": row.id,
                "original_filename": row.original_filename,
                "s3_key": row.s3_key,
                "content_type": row.content_type,
                "size_bytes": row.size_bytes,
                "download_url": url,
            }
        )

    return result