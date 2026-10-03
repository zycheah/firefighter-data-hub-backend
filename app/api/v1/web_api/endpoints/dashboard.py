from fastapi import APIRouter, Depends, HTTPException 
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import decode_access_token

#Models
from app.models.userModel import UserModel
from app.models.userProfileModel import UserProfileModel
from app.models.userResearcherModel import UserResearcherModel

dashboard = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/web_api/auth/login")

@dashboard.get("/summary")
def get_summary(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    data = decode_access_token(token)
    user = db.query(UserResearcherModel).filter(UserResearcherModel.id == data.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if( user.refresh_token != token):
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    totalFirefighters = db.query(UserModel).filter(UserModel.role == "firefighter").count()
    totalChiefs = db.query(UserModel).filter(UserModel.role == "chief").count()
    totalFireStations = (
        db.query(func.count(func.distinct(UserProfileModel.firefighter_station_name)))
        .join(UserModel, UserModel.id == UserProfileModel.user_id)
        .filter(UserModel.role.in_(["firefighter", "chief"]))
        .filter(UserProfileModel.firefighter_station_name.isnot(None))
        .scalar()
    )

    return {
        "totalFirefighters":totalFirefighters,
        "totalChiefs": totalChiefs,
        "totalFireStations": totalFireStations
    }