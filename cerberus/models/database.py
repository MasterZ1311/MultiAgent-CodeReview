"""
SQLAlchemy Async ORM Database Models for Cerberus.
Compatible with SQLite (local development) and PostgreSQL (production).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class CodeReviewRecord(Base):
    __tablename__ = "code_reviews"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    github_pr_url = Column(String(500), nullable=True)
    github_repo_owner = Column(String(255), nullable=True)
    github_repo_name = Column(String(255), nullable=True)
    commit_hash = Column(String(64), nullable=True)
    code_snippet = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    status = Column(String(20), default="processing")  # processing, completed, failed
    overall_score = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    results_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    findings = relationship("FindingRecord", back_populates="review", cascade="all, delete-orphan")
    feedback = relationship("ReviewFeedbackRecord", back_populates="review", uselist=False)


class FindingRecord(Base):
    __tablename__ = "review_findings"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    review_id = Column(String(64), ForeignKey("code_reviews.id"), index=True)
    agent_name = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    line_number = Column(Integer, nullable=True)
    column_number = Column(Integer, nullable=True)
    code_snippet = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    cwe_id = Column(String(20), nullable=True)
    cvss_score = Column(Float, nullable=True)
    exploitability_score = Column(Float, nullable=True)
    false_positive_probability = Column(Float, default=0.02)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    review = relationship("CodeReviewRecord", back_populates="findings")


class ReviewFeedbackRecord(Base):
    __tablename__ = "review_feedback"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    review_id = Column(String(64), ForeignKey("code_reviews.id"), unique=True)
    user_id = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=False)
    is_helpful = Column(Boolean, default=True)
    false_positives = Column(Integer, default=0)
    false_negatives = Column(Integer, default=0)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    review = relationship("CodeReviewRecord", back_populates="feedback")


class ApiKeyRecord(Base):
    __tablename__ = "api_keys"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    key_hash = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    prefix = Column(String(16), nullable=False)
    scopes = Column(String(255), default="review:read,review:write")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
