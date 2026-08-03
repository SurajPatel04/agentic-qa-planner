import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import ReviewAction

if TYPE_CHECKING:
    from app.models.test_case import TestCase


class TestReview(Base):
    __tablename__ = "test_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[ReviewAction] = mapped_column(
        SQLEnum(ReviewAction, native_enum=False), nullable=False
    )  # APPROVED, REJECTED, EDITED, PRIORITY_CHANGED, STATUS_CHANGED
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    new_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    test_case: Mapped["TestCase"] = relationship(
        "TestCase", back_populates="reviews"
    )
