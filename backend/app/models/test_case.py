import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import TestCategory, TestPriority, TestStatus, TestType

if TYPE_CHECKING:
    from app.models.qa_plan import QAPlan
    from app.models.test_review import TestReview


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    qa_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    test_type: Mapped[TestType] = mapped_column(
        SQLEnum(TestType, native_enum=False), nullable=False
    )  # UNIT, API, INTEGRATION, E2E, PLAYWRIGHT, MANUAL
    category: Mapped[TestCategory] = mapped_column(
        SQLEnum(TestCategory, native_enum=False), nullable=False
    )  # HAPPY_PATH, EDGE_CASE, PERMISSION, FAILURE_STATE, REGRESSION
    acceptance_criteria_ids: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )  # List of AC identifiers e.g. ["AC1", "AC3"]
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )  # List of step descriptions
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    preconditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TestStatus] = mapped_column(
        SQLEnum(TestStatus, native_enum=False),
        nullable=False,
        default=TestStatus.PROPOSED,
    )  # PROPOSED, APPROVED, REJECTED, EDITED
    priority: Mapped[TestPriority] = mapped_column(
        SQLEnum(TestPriority, native_enum=False),
        nullable=False,
        default=TestPriority.MEDIUM,
    )  # CRITICAL, HIGH, MEDIUM, LOW
    is_duplicate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_incomplete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    qa_plan: Mapped["QAPlan"] = relationship("QAPlan", back_populates="test_cases")
    reviews: Mapped[List["TestReview"]] = relationship(
        "TestReview",
        back_populates="test_case",
        cascade="all, delete-orphan",
        order_by="TestReview.created_at.desc()",
    )
