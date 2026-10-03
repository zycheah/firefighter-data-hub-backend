import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import decode_access_token
from app.models.locationModel import LocationEntryModel
from app.models.userResearcherModel import UserResearcherModel

export_table_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/web_api/auth/login")


@export_table_router.get("/export-csv")
def export_locations_csv(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    data = decode_access_token(token)
    user = db.query(UserResearcherModel).filter(UserResearcherModel.id == data.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Invalid Token")

    rows = db.scalars(select(LocationEntryModel)).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "user_id",
            "latitude",
            "longitude",
            "timestamp",
            "locationTimestamp",
            "accuracy",
            "altitude",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.user_id,
                row.latitude,
                row.longitude,
                row.timestamp.isoformat() if row.timestamp is not None else "",
                row.locationTimestamp.isoformat() if row.locationTimestamp is not None else "",
                "" if row.accuracy is None else row.accuracy,
                "" if row.altitude is None else row.altitude,
            ]
        )

    csv_bytes = buffer.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="locations_data.csv"',
        },
    )
