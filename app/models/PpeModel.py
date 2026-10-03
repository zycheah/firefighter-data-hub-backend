import uuid
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.db.base import Base


class PpeModel(Base):
    __tablename__ = "ppe_table"

    ppe_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("log_events.event_id", ondelete="SET NULL"), nullable=True)

    helmet_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    hood_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    face_mask_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    scba_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    glove_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    boot_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    bunker_coat_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    bunker_pants_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    is_ppe_updated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)