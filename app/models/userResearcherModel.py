import uuid
from typing import Optional

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserResearcherModel(Base):
    __tablename__ = "users_researcher"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=uuid.uuid4
    )

    first_name :Mapped[str] = mapped_column(String(20), unique=False, nullable= False)
    last_name :Mapped[str] = mapped_column(String(20), unique=False, nullable= True)


    university_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    personal_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    phonenumber: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # user role for authorization (researcher, researcher-admin)
    role: Mapped[str] = mapped_column(String(50), default="researcher", nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)

    is_active : Mapped[bool] = mapped_column(default=True)