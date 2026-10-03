import uuid
from typing import Optional

from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    phoneNumber: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    role: Mapped[str] = mapped_column(
        String(50),
        default="firefighter",
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)

    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    email_verified_at: Mapped[Optional[str]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile = relationship(
        "UserProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    locations = relationship(
        "LocationEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )