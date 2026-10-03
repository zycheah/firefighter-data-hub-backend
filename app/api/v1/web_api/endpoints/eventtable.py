import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import decode_access_token
from app.models.LogEventModel import LogEventModel
from app.models.userResearcherModel import UserResearcherModel
from app.api.v1.web_api.responseDTO.EventDataResponse import EventDataResponse


event_table_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/web_api/auth/login")


def _verify_researcher(token: str, db: Session) -> UserResearcherModel:
    data = decode_access_token(token)
    user = db.query(UserResearcherModel).filter(UserResearcherModel.id == data.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Match existing web_api token verification style
    if user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Invalid Token")

    return user


@event_table_router.get("/eventdata", response_model=EventDataResponse)
def get_event_data(
    limit: int,
    page: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    _verify_researcher(token, db)

    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    offset_data = (page - 1) * limit

    stmt = (
        select(LogEventModel)
        .order_by(LogEventModel.event_date.desc())
        .limit(limit)
        .offset(offset_data)
    )
    count_stmt = select(func.count()).select_from(LogEventModel)

    results = db.scalars(stmt).all()
    count = db.scalar(count_stmt)

    return {"count": count, "results": results}


@event_table_router.get("/export-event-data")
def export_event_data_csv(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    _verify_researcher(token, db)

    rows = db.scalars(select(LogEventModel).order_by(LogEventModel.event_date.desc())).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "event_id",
            "user_id",
            "event_date",
            "event_address",
            "is_same_ppe",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                str(row.event_id),
                row.user_id,
                row.event_date.isoformat() if row.event_date is not None else "",
                row.event_address,
                row.is_same_ppe,
            ]
        )

    csv_bytes = buffer.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="event_data.csv"'},
    )

