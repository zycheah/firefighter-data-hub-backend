from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_db, get_current_user
from app.models.location_entry import LocationEntry
from app.models.userModel import UserModel
from app.schemas.location import LocationItem

router = APIRouter()


@router.post("/bulk")
def upload_locations(
    payload: list[LocationItem],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    rows = []
    for item in payload:
        row = LocationEntry(
            user_id=current_user.id,
            latitude=item.latitude,
            longitude=item.longitude,
            accuracy_m=item.accuracy_m,
            recorded_at=item.recorded_at,
        )
        rows.append(row)

    db.add_all(rows)
    db.commit()

    return {"message": "Locations uploaded", "count": len(rows)}