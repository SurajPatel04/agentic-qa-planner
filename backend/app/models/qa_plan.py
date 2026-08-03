import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import PlanStatus

if TYPE_CHECKING:
    from app.models.acceptance_criteria import AcceptanceCriteria
    from app.models.execution_log import ExecutionLog
    from app.models.qa_plan_version import QAPlanVersion
    from app.models.test_case import TestCase


class QAPlan(Base):
    __tablename__ = "qa_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_or_user_story: Mapped[str] = mapped_column(Text, nullable=False)
    implementation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assumptions: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    status: Mapped[PlanStatus] = mapped_column(
        SQLEnum(PlanStatus, native_enum=False),
        nullable=False,
        default=PlanStatus.DRAFT,
    )  # draft, reviewed, approved, archived
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    coverage_summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
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
    acceptance_criteria: Mapped[List["AcceptanceCriteria"]] = relationship(
        "AcceptanceCriteria",
        back_populates="qa_plan",
        cascade="all, delete-orphan",
        order_by="AcceptanceCriteria.identifier",
    )
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase",
        back_populates="qa_plan",
        cascade="all, delete-orphan",
        order_by="TestCase.created_at",
    )
    versions: Mapped[List["QAPlanVersion"]] = relationship(
        "QAPlanVersion",
        back_populates="qa_plan",
        cascade="all, delete-orphan",
        order_by="QAPlanVersion.version_number.desc()",
    )
    execution_logs: Mapped[List["ExecutionLog"]] = relationship(
        "ExecutionLog",
        back_populates="qa_plan",
        cascade="all, delete-orphan",
        order_by="ExecutionLog.created_at",
    )
