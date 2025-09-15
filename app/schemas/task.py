from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


Priority = Literal["low", "med", "high"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = "med"
    tags: list[str] = Field(default_factory=list)

    @field_validator("due_date")
    @classmethod
    def ensure_utc(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        # Require timezone-aware and explicitly UTC
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("due_date must include timezone (UTC)")
        if v.astimezone(timezone.utc).utcoffset() != timezone.utc.utcoffset(v):
            # If provided tz isn't UTC, reject
            raise ValueError("due_date must be in UTC (e.g., 2025-09-15T12:00:00Z)")
        # Normalize to UTC to ensure consistent serialization
        return v.astimezone(timezone.utc)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must be non-empty")
        return v


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    status: Literal["todo", "in_progress", "done"] = "todo"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
