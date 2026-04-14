"""
Models package - import all models so SQLAlchemy registers them with Base.metadata
"""
from app.db.base import Base  # noqa
from app.models.models import (  # noqa
    User,
    Resume,
    UserPreferences,
    Job,
    JobScore,
    Application,
    EmploymentType,
    WorkMode,
    SponsorshipStatus,
    ApplicationStatus,
    ExperienceLevel,
)

# Convenience re-exports
__all__ = [
    "Base",
    "User",
    "Resume",
    "UserPreferences",
    "Job",
    "JobScore",
    "Application",
    "EmploymentType",
    "WorkMode",
    "SponsorshipStatus",
    "ApplicationStatus",
    "ExperienceLevel",
]
