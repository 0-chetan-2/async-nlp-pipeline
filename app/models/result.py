from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    
from app.models.base import Base
from sqlalchemy.orm import relationship


class Result(Base):
    __tablename__ = "results"

    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.task_id"),
        primary_key=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="result",
    )