from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class CollectedItem(BaseModel):
    source_id: str
    url: HttpUrl
    title: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    raw: Optional[Dict[str, Any]] = None


class StandardTask(BaseModel):
    external_source_id: str = Field(description="Deterministic id from source, e.g., hash(url)")
    title: str
    description: str
    priority: str = Field(default="medium")
    status: str = Field(default="not_started")
    source_url: HttpUrl
    source_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = Field(default_factory=dict)


class PublishResult(BaseModel):
    success: bool
    task_id: Optional[str] = None
    error: Optional[str] = None