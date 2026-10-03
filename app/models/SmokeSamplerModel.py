import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SmokeSamplerSubmissionModel(Base):
    __tablename__ = "smoke_sampler_submissions"

    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SmokeSamplerSampleModel(Base):
    __tablename__ = "smoke_sampler_samples"

    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("smoke_sampler_submissions.submission_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chemical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    percentage_proportion: Mapped[float] = mapped_column(Float, nullable=False)