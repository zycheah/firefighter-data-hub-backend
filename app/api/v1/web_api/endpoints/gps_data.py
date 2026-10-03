from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.deps import get_db

from app.models.locationModel import LocationEntryModel

from app.api.v1.web_api.responseDTO.LocationDataResponse import LocationDataResponse

send_location_router = APIRouter()

@send_location_router.get("/tabledata", response_model=LocationDataResponse)
def gps_data_transfer(limit: int, page : int, db:Session = Depends(get_db)):
    offset_data = 0
    if (page > 1 ):
        offset_data = (page - 1)*limit

    stmt = select(LocationEntryModel).limit(limit).offset(offset_data)
    count_stmt = select(func.count()).select_from(LocationEntryModel)

    results = db.scalars(stmt).all()
    count = db.scalar(count_stmt)


    return {
        "count": count,
        "results": results
    }