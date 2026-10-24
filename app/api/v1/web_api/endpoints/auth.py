from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

# DB Models
from app.models.userResearcherModel import UserResearcherModel

# Request DTO
from app.api.v1.web_api.requestDTO.loginRequestDTO import LoginRequestDTO
from app.api.v1.web_api.requestDTO.registerRequestDTO import RegisterRequestDTO
from app.api.v1.web_api.requestDTO.updateMeRequestDTO import UpdateMeRequestDTO
from app.api.v1.web_api.requestDTO.passwordResetRequestDTO import PasswordResetRequestDTO
#Response DTO
from app.api.v1.web_api.responseDTO.loginResponseDTO import LoginResponseDTO

web_auth = APIRouter()
oauth2_web_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/web_api/auth/login")


def get_current_researcher(
    token: str = Depends(oauth2_web_scheme),
    db: Session = Depends(get_db),
) -> UserResearcherModel:
    payload = decode_access_token(token)
    user = db.query(UserResearcherModel).filter(UserResearcherModel.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _to_frontend_researcher_role(role: str) -> str:
    normalized = (role or "").lower().replace("-", "_").replace(" ", "_")
    if "admin" in normalized:
        return "RESEARCH_ADMIN"
    return "RESEARCHER"


@web_auth.get("/me")
def me(current: UserResearcherModel = Depends(get_current_researcher)):
    return {
        "id": str(current.id),
        "firstName": current.first_name,
        "lastName": current.last_name or "",
        "universityEmail": current.university_email,
        "personalEmail": current.personal_email,
        "role": _to_frontend_researcher_role(current.role),
        "phoneNumber": current.phonenumber,
    }


@web_auth.put("/me")
def update_me(
    payload: UpdateMeRequestDTO,
    current: UserResearcherModel = Depends(get_current_researcher),
    db: Session = Depends(get_db),
):
    if payload.personal_email is not None:
        existing = (
            db.query(UserResearcherModel)
            .filter(
                UserResearcherModel.personal_email == str(payload.personal_email),
                UserResearcherModel.id != current.id,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Personal email already in use")

    if payload.first_name is not None:
        current.first_name = payload.first_name
    if payload.last_name is not None:
        current.last_name = payload.last_name
    if payload.personal_email is not None:
        current.personal_email = str(payload.personal_email)
    if payload.phoneNumber is not None:
        current.phonenumber = payload.phoneNumber

    db.commit()
    db.refresh(current)

    return {
        "id": str(current.id),
        "firstName": current.first_name,
        "lastName": current.last_name or "",
        "universityEmail": current.university_email,
        "personalEmail": current.personal_email,
        "role": _to_frontend_researcher_role(current.role),
        "phoneNumber": current.phonenumber,
    }


@web_auth.post("/password-reset")
def password_reset(
    payload: PasswordResetRequestDTO,
    current: UserResearcherModel = Depends(get_current_researcher),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.password, current.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    current.password_hash = hash_password(payload.newPassword)
    db.commit()
    return {"ok": True}


@web_auth.post("/login")
def login(payload: LoginRequestDTO, db : Session = Depends(get_db)):
    user = db.query(UserResearcherModel).filter(UserResearcherModel.university_email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Users credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending approval")
    
    token = create_access_token(subject=user.id, role=user.role)
    user.refresh_token = token

    db.commit()
    
    return {
        "access_token": token, 
        "token_type": "bearer"
    }

@web_auth.post("/register")
def register(payload :RegisterRequestDTO, db:Session = Depends(get_db) ):
    existing = db.query(UserResearcherModel).filter(UserResearcherModel.university_email == payload.university_email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserResearcherModel(
        first_name = payload.first_name,
        last_name = payload.last_name,
        university_email = payload.university_email,
        personal_email = payload.personal_email,
        password_hash=hash_password(payload.password),
        role=payload.role.lower(),
        phonenumber=payload.phoneNumber,
        # Researcher accounts are approved by an administrator before first sign-in.
        is_active=False,
    )

    db.add(user)
    db.flush()

    db.commit()

    return status.HTTP_201_CREATED