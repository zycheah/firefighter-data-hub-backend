from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from jose import jwt, JWTError

from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends

from app.core.deps import get_db
from app.models.userModel import UserModel
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": str(subject), "role": str(role), "exp": expire}
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    
 	

def verify_refresh_token(token : str, db: Session = Depends(get_db)):

    try:
        payload = decode_access_token(token)
        print("decoded token", payload)

        user_id = payload.get("sub")

        user_role = payload.get("role")

        if user_id is None or user_role is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        db_model = db.query(UserModel).filter(UserModel.id == user_id).first()

        if db_model.refresh_token is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            if db_model.refresh_token != token or db_model.role != user_role:
                raise HTTPException(status_code=401, detail="Invalid token")  
        return db_model

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")	
	

def create_refresh_token(token:str, db:Session = Depends(get_db)):
    userModel = verify_refresh_token(token, db)
    new_token = create_access_token(subject=str(userModel.id), role=userModel.role)
    
    userModel.refresh_token = new_token
    db.commit()
    
    return new_token

def verify_reset_password(token: str, current_password : str, new_password: str, db: Session = Depends(get_db)):
    try:
        user_model = verify_refresh_token(token=token, db=db)

        if not verify_password(current_password, user_model.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        new_token = create_access_token(subject=str(user_model.id), role=user_model.role)

        user_model.refresh_token = new_token
        user_model.password_hash = hash_password(new_password)
        
        db.commit()

        return new_token


    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

