import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.qa_plan import QAPlan


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    qa_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "Retriever", "LLMGenerator", "CoverageEngine"
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="INFO"
    )  # "SUCCESS", "WARNING", "FAILED", "INFO"
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )  # Structured extra metadata/payload
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    qa_plan: Mapped["QAPlan"] = relationship(
        "QAPlan", back_populates="execution_logs"
    )
