from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base


class SourceItem(Base):
    __tablename__ = "source_items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(100), index=True, nullable=False)
    source_url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)
    raw_content = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("source_id", "content_hash", name="uq_sourceitem_source_hash"),
    )


class GeneratedTask(Base):
    __tablename__ = "generated_tasks"

    id = Column(Integer, primary_key=True, index=True)
    external_source_id = Column(String(128), index=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    published_task_id = Column(String(64), nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("external_source_id", name="uq_generatedtask_external_source_id"),
    )