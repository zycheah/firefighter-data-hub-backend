import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import verify_refresh_token, create_refresh_token

from app.models.LogEventModel import LogEventModel
from app.models.PpeModel import PpeModel

from app.api.v1.dtos.LogEvent import LogEventDTO
from app.api.v1.dtos.Ppe import PpeDTO


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/ppe", status_code=status.HTTP_201_CREATED)
def ppe_data_transfer(
    payload: PpeDTO,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    current_user = verify_refresh_token(token=token, db=db)

    event_uuid = None

    if payload.event_id:
        try:
            event_uuid = uuid.UUID(str(payload.event_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event_id format",
            )

    elif payload.is_ppe_updated:
        latest_event = (
            db.query(LogEventModel)
            .filter(LogEventModel.user_id == current_user.id)
            .order_by(LogEventModel.created_at.desc())
            .first()
        )

        if not latest_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No log event found to associate PPE update with",
            )

        event_uuid = latest_event.event_id

    ppe_data = PpeModel(
        user_id=current_user.id,
        event_id=event_uuid,
        helmet_id=payload.helmet_id.strip(),
        hood_id=payload.hood_id.strip(),
        face_mask_id=payload.face_mask_id.strip(),
        scba_id=payload.scba_id.strip(),
        glove_id=payload.glove_id.strip(),
        boot_id=payload.boot_id.strip(),
        bunker_coat_id=payload.bunker_coat_id.strip(),
        bunker_pants_id=payload.bunker_pants_id.strip(),
        is_ppe_updated=payload.is_ppe_updated,
    )

    db.add(ppe_data)
    db.commit()
    db.refresh(ppe_data)

    new_token = create_refresh_token(token=token, db=db)

    return {
        "message": "PPE data saved successfully",
        "ppe_id": str(getattr(ppe_data, "ppe_id", "")),
        "event_id": str(ppe_data.event_id) if ppe_data.event_id else None,
        "access_token": new_token,
        "token_type": "bearer",
    }


@router.post("/logevent", status_code=status.HTTP_201_CREATED)
def logevent_transfer(
    payload: LogEventDTO,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    current_user = verify_refresh_token(token=token, db=db)

    d = payload.event_date
    event_dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)

    log_event = LogEventModel(
        user_id=current_user.id,
        event_date=event_dt,
        event_address=payload.event_address.strip(),
        is_same_ppe=payload.is_same_ppe,
    )

    db.add(log_event)
    db.commit()
    db.refresh(log_event)

    new_token = create_refresh_token(token=token, db=db)

    return {
        "message": "Log event saved successfully",
        "event_id": str(log_event.event_id),
        "access_token": new_token,
        "token_type": "bearer",
    }