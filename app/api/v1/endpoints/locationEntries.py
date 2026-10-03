from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.v1.dtos.LocationEntriesDTO import LocationEntryDTO
from app.core.deps import get_db
from app.core.security import decode_access_token, verify_refresh_token
from app.models.locationModel import LocationEntryModel

locationEntries_Router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@locationEntries_Router.post("/")
def create_location_entry(
    payload: list[LocationEntryDTO],
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_token_info = decode_access_token(token)
    verify_refresh_token(token, db)

    user_id = user_token_info.get("sub")

    user_location_entries = []

    for entry in payload:
        location_timestamp = (
            entry.locationTimestamp
            or entry.timestamp
            or datetime.now(timezone.utc)
        )

        l_entry = LocationEntryModel(
            user_id=user_id,
            latitude=entry.latitude,
            longitude=entry.longitude,
            locationTimestamp=location_timestamp,
            accuracy=entry.accuracy,
            altitude=entry.altitude,
            timestamp=datetime.now(timezone.utc),
        )

        user_location_entries.append(l_entry)

    db.add_all(user_location_entries)
    db.commit()

    return Response(status_code=201, content="Location entries created")


@locationEntries_Router.get("/last")
def get_last_location_entries(
    limit: int = Query(default=10, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_token_info = decode_access_token(token)
    verify_refresh_token(token, db)

    user_id = user_token_info.get("sub")

    rows = (
        db.query(LocationEntryModel)
        .filter(LocationEntryModel.user_id == user_id)
        .order_by(LocationEntryModel.locationTimestamp.desc())
        .limit(limit)
        .all()
    )

    results = [
        {
            "id": str(row.id),
            "user_id": str(row.user_id),
            "latitude": row.latitude,
            "longitude": row.longitude,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "locationTimestamp": row.locationTimestamp.isoformat()
            if row.locationTimestamp
            else None,
            "accuracy": row.accuracy,
            "altitude": row.altitude,
        }
        for row in rows
    ]

    return {
        "results": results,
        "count": len(results),
    }