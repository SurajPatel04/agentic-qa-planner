import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.qa_plan import QAPlan


class AcceptanceCriteria(Base):
    __tablename__ = "acceptance_criteria"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    qa_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    identifier: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "AC1", "AC2"
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    qa_plan: Mapped["QAPlan"] = relationship(
        "QAPlan", back_populates="acceptance_criteria"
    )
