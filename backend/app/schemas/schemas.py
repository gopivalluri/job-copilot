"""
Pydantic v2 schemas for request/response validation
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.models import (
    ApplicationStatus, EmploymentType, ExperienceLevel,
    SponsorshipStatus, WorkMode
)


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: Optional[datetime]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── Resume ───────────────────────────────────────────────────────────────────

class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: Optional[str]
    parsed_data: Optional[Dict[str, Any]]
    is_active: bool
    created_at: Optional[datetime]


class ParsedResume(BaseModel):
    """Structured resume data after parsing"""
    skills: List[str] = []
    experience_years: Optional[float] = None
    current_title: Optional[str] = None
    education: List[Dict[str, str]] = []
    experience: List[Dict[str, Any]] = []
    summary: Optional[str] = None


# ─── Preferences ──────────────────────────────────────────────────────────────

class PreferencesCreate(BaseModel):
    target_roles: List[str] = []
    employment_types: List[str] = []
    work_modes: List[str] = []
    preferred_locations: List[str] = []
    min_salary: int = Field(default=0, ge=0)
    max_salary: Optional[int] = None
    requires_sponsorship: bool = False
    sponsorship_types: List[str] = []
    experience_levels: List[str] = []
    include_keywords: List[str] = []
    exclude_keywords: List[str] = []
    auto_score_threshold: int = Field(default=75, ge=0, le=100)
    daily_limit: int = Field(default=50, ge=1, le=200)


class PreferencesOut(PreferencesCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


# ─── Job ──────────────────────────────────────────────────────────────────────

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: Optional[str]
    source: Optional[str]
    source_url: Optional[str]
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]
    employment_type: Optional[EmploymentType]
    work_mode: Optional[WorkMode]
    experience_level: Optional[ExperienceLevel]
    skills_required: List[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    sponsorship_status: Optional[SponsorshipStatus]
    posted_at: Optional[datetime]
    ingested_at: Optional[datetime]


class JobWithScore(JobOut):
    score: Optional[float] = None
    score_details: Optional[Dict[str, float]] = None
    is_filtered_out: bool = False
    filter_reason: Optional[str] = None


class JobIngest(BaseModel):
    """Manual job ingestion payload"""
    title: str
    company: str
    location: Optional[str] = None
    description: str
    source_url: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_mode: Optional[WorkMode] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


# ─── Score ────────────────────────────────────────────────────────────────────

class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: int
    total_score: float
    title_score: float
    skills_score: float
    sponsorship_score: float
    employment_score: float
    location_score: float
    experience_score: float
    is_filtered_out: bool
    filter_reason: Optional[str]


# ─── AI Tailor ────────────────────────────────────────────────────────────────

class TailorRequest(BaseModel):
    job_id: int
    generate_cover_letter: bool = True


class TailorResponse(BaseModel):
    tailored_resume: str
    cover_letter: Optional[str]
    key_matches: List[str]
    suggestions: List[str]


# ─── Application ──────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    offer_details: Optional[Dict[str, Any]] = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    status: ApplicationStatus
    tailored_resume: Optional[str]
    cover_letter: Optional[str]
    notes: Optional[str]
    applied_at: Optional[datetime]
    last_updated: Optional[datetime]
    follow_up_date: Optional[datetime]
    offer_details: Optional[Dict[str, Any]]
    job: Optional[JobOut] = None


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_jobs_ingested: int
    jobs_scored_today: int
    top_matches: List[JobWithScore]
    applications_by_status: Dict[str, int]
    total_applications: int
    applied_today: int
    avg_match_score: float
    sponsorship_eligible: int
