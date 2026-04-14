"""
Database Models - all ORM models for Job Application Copilot
Imported in models/__init__.py to register with SQLAlchemy metadata
"""
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, JSON, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    contract  = "contract"
    part_time = "part_time"
    internship = "internship"

class WorkMode(str, enum.Enum):
    remote  = "remote"
    hybrid  = "hybrid"
    onsite  = "onsite"

class SponsorshipStatus(str, enum.Enum):
    available    = "available"
    not_available = "not_available"
    unknown      = "unknown"
    transfer_ok  = "transfer_ok"

class ApplicationStatus(str, enum.Enum):
    saved      = "saved"
    applied    = "applied"
    interviewing = "interviewing"
    offer      = "offer"
    rejected   = "rejected"
    withdrawn  = "withdrawn"

class ExperienceLevel(str, enum.Enum):
    entry  = "entry"
    mid    = "mid"
    senior = "senior"
    lead   = "lead"
    staff  = "staff"


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name     = Column(String(255))
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resumes       = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    preferences   = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications  = relationship("Application", back_populates="user", cascade="all, delete-orphan")


# ─── Resume ───────────────────────────────────────────────────────────────────

class Resume(Base):
    __tablename__ = "resumes"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename      = Column(String(255))
    file_path     = Column(String(512))
    raw_text      = Column(Text)                # extracted plain text
    parsed_data   = Column(JSON)                # structured: skills, experience, education
    is_active     = Column(Boolean, default=True)  # active/primary resume
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    user          = relationship("User", back_populates="resumes")


# ─── User Preferences ─────────────────────────────────────────────────────────

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Target roles (stored as JSON array)
    target_roles         = Column(JSON, default=list)           # ["Software Engineer", "Backend Engineer"]

    # Employment filters
    employment_types     = Column(JSON, default=list)           # ["full_time", "contract"]
    work_modes           = Column(JSON, default=list)           # ["remote", "hybrid"]
    preferred_locations  = Column(JSON, default=list)           # ["Texas", "California", "Remote"]

    # Compensation
    min_salary           = Column(Integer, default=0)           # annual USD
    max_salary           = Column(Integer, nullable=True)

    # Sponsorship
    requires_sponsorship = Column(Boolean, default=False)
    sponsorship_types    = Column(JSON, default=list)           # ["H1B", "H1B_transfer"]

    # Experience
    experience_levels    = Column(JSON, default=list)           # ["mid", "senior"]

    # Keyword filters
    include_keywords     = Column(JSON, default=list)           # boost if present
    exclude_keywords     = Column(JSON, default=list)           # filter out if present

    # Auto-apply threshold (0-100)
    auto_score_threshold = Column(Integer, default=75)

    # Daily application limit
    daily_limit          = Column(Integer, default=50)

    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="preferences")


# ─── Job ──────────────────────────────────────────────────────────────────────

class Job(Base):
    __tablename__ = "jobs"

    id                 = Column(Integer, primary_key=True, index=True)
    external_id        = Column(String(255), index=True)          # ID from source
    source             = Column(String(100), index=True)          # e.g. "remotive", "mock"
    source_url         = Column(String(1024))

    # Core fields
    title              = Column(String(512), nullable=False)
    company            = Column(String(255), nullable=False)
    location           = Column(String(255))
    description        = Column(Text)
    requirements       = Column(Text)

    # Normalized / structured
    employment_type    = Column(Enum(EmploymentType), nullable=True)
    work_mode          = Column(Enum(WorkMode), nullable=True)
    experience_level   = Column(Enum(ExperienceLevel), nullable=True)
    skills_required    = Column(JSON, default=list)               # ["Python", "FastAPI"]
    salary_min         = Column(Integer, nullable=True)
    salary_max         = Column(Integer, nullable=True)
    salary_currency    = Column(String(10), default="USD")

    # Sponsorship
    sponsorship_status = Column(Enum(SponsorshipStatus), default=SponsorshipStatus.unknown)
    sponsorship_notes  = Column(Text, nullable=True)

    # Metadata
    posted_at          = Column(DateTime(timezone=True), nullable=True)
    ingested_at        = Column(DateTime(timezone=True), server_default=func.now())
    is_active          = Column(Boolean, default=True)

    # Unique constraint: same job from same source
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )

    # Relationships
    scores       = relationship("JobScore", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job")


# ─── Job Score ────────────────────────────────────────────────────────────────

class JobScore(Base):
    __tablename__ = "job_scores"

    id              = Column(Integer, primary_key=True, index=True)
    job_id          = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Composite score (0-100)
    total_score     = Column(Float, nullable=False)

    # Factor breakdown
    title_score       = Column(Float, default=0)
    skills_score      = Column(Float, default=0)
    sponsorship_score = Column(Float, default=0)
    employment_score  = Column(Float, default=0)
    location_score    = Column(Float, default=0)
    experience_score  = Column(Float, default=0)

    # Filter flags
    is_filtered_out   = Column(Boolean, default=False)
    filter_reason     = Column(String(512), nullable=True)

    scored_at         = Column(DateTime(timezone=True), server_default=func.now())

    job  = relationship("Job", back_populates="scores")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("job_id", "user_id", name="uq_job_user_score"),
    )


# ─── Application ──────────────────────────────────────────────────────────────

class Application(Base):
    __tablename__ = "applications"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id          = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    status          = Column(Enum(ApplicationStatus), default=ApplicationStatus.saved)

    # AI-tailored content
    tailored_resume = Column(Text, nullable=True)
    cover_letter    = Column(Text, nullable=True)

    # Tracking
    applied_at      = Column(DateTime(timezone=True), nullable=True)
    last_updated    = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    notes           = Column(Text, nullable=True)
    follow_up_date  = Column(DateTime(timezone=True), nullable=True)

    # Responses
    interview_dates = Column(JSON, default=list)
    offer_details   = Column(JSON, nullable=True)   # {salary, equity, benefits}

    user = relationship("User", back_populates="applications")
    job  = relationship("Job", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )
