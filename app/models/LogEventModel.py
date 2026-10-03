import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogEventModel(Base):
    __tablename__ = "log_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    event_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_address: Mapped[str] = mapped_column(String(255), nullable=False)
    is_same_ppe: Mapped[bool] = mapped_column(Boolean, nullable=False)