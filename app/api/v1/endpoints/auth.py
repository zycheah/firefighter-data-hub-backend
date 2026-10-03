from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from itsdangerous import BadSignature, SignatureExpired

from app.db.session import SessionLocal
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    verify_refresh_token,
    create_refresh_token,
    verify_reset_password,
)

from app.models.userModel import UserModel
from app.models.userProfileModel import UserProfileModel
from app.models.locationModel import LocationEntryModel
from app.models.LogEventModel import LogEventModel
from app.models.PpeModel import PpeModel
from app.models.SmokeSamplerModel import (
    SmokeSamplerSubmissionModel,
    SmokeSamplerSampleModel,
)

# Optional EC2/S3 proof-of-concept models.
# These imports are used only if those tables/models exist in your current project.
try:
    from app.models.location_entry import LocationEntry
except Exception:
    LocationEntry = None

try:
    from app.models.uploaded_file import UploadedFile
except Exception:
    UploadedFile = None

from app.api.v1.dtos.UserRegister import UserRegisterDTO
from app.api.v1.dtos.UserLogin import UserLoginDTO
from app.api.v1.dtos.UserPasswordResetDTO import PasswordResetDTO
from app.api.v1.dtos.VerifyEmailDTO import VerifyEmailDTO
from app.api.v1.dtos.ResendVerification import ResendVerificationDTO
from app.api.v1.dtos.DeleteAccountDTO import DeleteAccountDTO
from app.api.v1.dtos.ForgotPasswordDTO import (
    ForgotPasswordRequestDTO,
    ForgotPasswordConfirmDTO,
)

from app.schemas.auth import TokenResponse

from app.services.email_service import email_service
from app.services.email_token_service import email_token_service


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _profile_name(user: UserModel) -> str:
    if user.profile and user.profile.full_name:
        return user.profile.full_name
    return "User"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    payload = decode_access_token(token)
    user = db.query(UserModel).filter(UserModel.id == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/register")
def register(
    payload: UserRegisterDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserModel(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        phoneNumber=payload.phoneNumber,
        is_email_verified=False,
        email_verified_at=None,
    )

    db.add(user)
    db.flush()

    profile = UserProfileModel(
        user_id=user.id,
        full_name=payload.full_name,
        gender=payload.gender,
        race=payload.race,
        ethnicity=payload.ethnicity,
        year_of_birth=payload.year_of_birth,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        dominant_hand=payload.dominant_hand,
        years_of_experience=payload.years_of_experience,
        firefighter_status=payload.firefighter_status,
        type_of_firefighter=payload.type_of_firefighter,
        firefighter_station_name=payload.firefighter_station_name,
        city=payload.city,
        state=payload.state,
    )

    db.add(profile)
    db.commit()
    db.refresh(user)

    token = email_token_service.generate_verify_email_token(
        user_id=str(user.id),
        email=user.email,
    )

    background_tasks.add_task(
        email_service.send_verification_email,
        user.email,
        profile.full_name,
        token,
    )

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "is_email_verified": user.is_email_verified,
        "message": "Account created successfully. Please verify your email before signing in.",
    }


@router.post("/verify-email")
def verify_email(
    payload: VerifyEmailDTO,
    db: Session = Depends(get_db),
):
    try:
        token_payload = email_token_service.verify_email_token(
            payload.token,
            max_age_seconds=86400,
        )
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Verification token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    if token_payload.get("purpose") != "verify_email":
        raise HTTPException(status_code=400, detail="Invalid token purpose")

    user = db.query(UserModel).filter(UserModel.id == token_payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email != token_payload.get("email"):
        raise HTTPException(status_code=400, detail="Token email does not match user")

    if user.is_email_verified:
        return {"message": "Email is already verified"}

    user.is_email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)

    db.add(user)
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(
    payload: ResendVerificationDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_email_verified:
        return {"message": "Email is already verified"}

    token = email_token_service.generate_verify_email_token(
        user_id=str(user.id),
        email=user.email,
    )

    background_tasks.add_task(
        email_service.send_verification_email,
        user.email,
        _profile_name(user),
        token,
    )

    return {"message": "Verification email sent"}


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLoginDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before signing in.",
        )

    token = create_access_token(subject=user.id, role=user.role)
    user.refresh_token = token

    db.commit()

    background_tasks.add_task(
        email_service.send_login_notification,
        user.email,
        _profile_name(user),
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    data = decode_access_token(token)
    user = db.query(UserModel).filter(UserModel.id == data.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    profile = user.profile

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": profile.full_name if profile else None,
        "phoneNumber": user.phoneNumber,
        "is_email_verified": user.is_email_verified,
        "email_verified_at": user.email_verified_at.isoformat()
        if user.email_verified_at
        else None,
        "full_name": profile.full_name if profile else None,
        "gender": profile.gender if profile else None,
        "race": profile.race if profile else None,
        "ethnicity": profile.ethnicity if profile else None,
        "year_of_birth": profile.year_of_birth if profile else None,
        "height_cm": profile.height_cm if profile else None,
        "weight_kg": profile.weight_kg if profile else None,
        "dominant_hand": profile.dominant_hand if profile else None,
        "Years_of_experience": profile.years_of_experience if profile else None,
        "firefighter_status": profile.firefighter_status if profile else None,
        "type_of_firefighter": profile.type_of_firefighter if profile else None,
        "firefighter_station_name": profile.firefighter_station_name if profile else None,
        "city": profile.city if profile else None,
        "state": profile.state if profile else None,
    }


@router.delete("/delete-account")
def delete_account(
    payload: DeleteAccountDTO,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = verify_refresh_token(token=token, db=db)

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    user_id = str(user.id)
    email = user.email
    full_name = _profile_name(user)

    try:
        # 1. Delete smoke sampler child rows first.
        submission_ids = [
            row.submission_id
            for row in db.query(SmokeSamplerSubmissionModel.submission_id)
            .filter(SmokeSamplerSubmissionModel.user_id == user_id)
            .all()
        ]

        if submission_ids:
            db.query(SmokeSamplerSampleModel).filter(
                SmokeSamplerSampleModel.submission_id.in_(submission_ids)
            ).delete(synchronize_session=False)

        db.query(SmokeSamplerSubmissionModel).filter(
            SmokeSamplerSubmissionModel.user_id == user_id
        ).delete(synchronize_session=False)

        # 2. Delete PPE before log events because PPE can reference event_id.
        db.query(PpeModel).filter(
            PpeModel.user_id == user_id
        ).delete(synchronize_session=False)

        db.query(LogEventModel).filter(
            LogEventModel.user_id == user_id
        ).delete(synchronize_session=False)

        # 3. Delete location records from the active location model.
        db.query(LocationEntryModel).filter(
            LocationEntryModel.user_id == user_id
        ).delete(synchronize_session=False)

        # 4. Delete optional EC2/S3 proof-of-concept location table if present.
        if LocationEntry is not None:
            db.query(LocationEntry).filter(
                LocationEntry.user_id == user_id
            ).delete(synchronize_session=False)

        # 5. Delete optional uploaded file metadata if present.
        if UploadedFile is not None:
            db.query(UploadedFile).filter(
                UploadedFile.user_id == user_id
            ).delete(synchronize_session=False)

        # 6. Delete profile explicitly, then the user.
        db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).delete(synchronize_session=False)

        db.delete(user)
        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Could not delete account: {str(exc)}",
        ) from exc

    background_tasks.add_task(
        email_service.send_account_deleted_notification,
        email,
        full_name,
    )

    return {"message": "Account deleted successfully"}


@router.post("/forgot-password/request")
def forgot_password_request(
    payload: ForgotPasswordRequestDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found for this email.",
        )

    background_tasks.add_task(
        email_service.send_password_reset_requested_notification,
        user.email,
        _profile_name(user),
    )

    return {
        "message": "Password change request initiated. Please continue to set your new password.",
    }


@router.post("/forgot-password/confirm")
def forgot_password_confirm(
    payload: ForgotPasswordConfirmDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found for this email.",
        )

    user.password_hash = hash_password(payload.newPassword)

    # Invalidate any stored token after password change.
    user.refresh_token = None

    db.add(user)
    db.commit()

    background_tasks.add_task(
        email_service.send_password_changed_notification,
        user.email,
        _profile_name(user),
    )

    return {
        "message": "Password updated successfully. You can now sign in with your new password.",
    }


@router.get("/test")
def testingRouter():
    return {
        "ok": True,
        "message": "Testing Router is Working!",
    }


@router.post("/password-reset")
def password_reset(
    payload: PasswordResetDTO,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    new_refresh_token = verify_reset_password(
        token,
        payload.password,
        payload.newPassword,
        db=db,
    )

    return {
        "access_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    refreshed_token = create_refresh_token(token=token, db=db)

    return {
        "access_token": refreshed_token,
        "token_type": "bearer",
    }