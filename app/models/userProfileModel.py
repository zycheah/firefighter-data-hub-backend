from __future__ import annotations

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    race: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ethnicity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year_of_birth: Mapped[str | None] = mapped_column(Integer, nullable=True)

    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    dominant_hand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    years_of_experience: Mapped[str | None] = mapped_column(String(100), nullable=True)

    firefighter_status: Mapped[str | None] = mapped_column(String(100), nullable=False)
    type_of_firefighter: Mapped[str | None] = mapped_column(String(150), nullable=False)
    firefighter_station_name: Mapped[str| None] = mapped_column(String(255), nullable=False)

    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user = relationship("UserModel", back_populates="profile")