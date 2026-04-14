"""
Job Filtering Engine
Applies user-defined preferences to determine if a job should be excluded.
Returns (passes: bool, reason: str | None)
"""
from typing import Optional, Tuple
import re

from app.models.models import Job, UserPreferences, SponsorshipStatus, WorkMode, EmploymentType


def normalize_text(text: str) -> str:
    return text.lower().strip() if text else ""


def job_passes_filters(
    job: Job,
    prefs: UserPreferences,
) -> Tuple[bool, Optional[str]]:
    """
    Returns (True, None) if the job passes all filters.
    Returns (False, reason) if the job should be excluded.
    """

    description_text = normalize_text((job.description or "") + " " + (job.requirements or ""))

    # ── 1. Exclude keywords ───────────────────────────────────────────────────
    for kw in (prefs.exclude_keywords or []):
        if re.search(re.escape(kw.lower()), description_text):
            return False, f"Contains excluded keyword: '{kw}'"

    # ── 2. Sponsorship filter ─────────────────────────────────────────────────
    if prefs.requires_sponsorship:
        if job.sponsorship_status == SponsorshipStatus.not_available:
            return False, "Sponsorship not available (explicitly stated)"

    # ── 3. Employment type filter ─────────────────────────────────────────────
    if prefs.employment_types and job.employment_type:
        allowed = [t.lower() for t in prefs.employment_types]
        if job.employment_type.value not in allowed:
            return False, f"Employment type '{job.employment_type.value}' not in preferred {prefs.employment_types}"

    # ── 4. Work mode filter ───────────────────────────────────────────────────
    if prefs.work_modes and job.work_mode:
        allowed_modes = [m.lower() for m in prefs.work_modes]
        if job.work_mode.value not in allowed_modes:
            return False, f"Work mode '{job.work_mode.value}' not in preferred {prefs.work_modes}"

    # ── 5. Salary filter ──────────────────────────────────────────────────────
    if prefs.min_salary and job.salary_max:
        # Only filter if the job's MAX salary is below user's minimum
        if job.salary_max < prefs.min_salary:
            return False, f"Max salary ${job.salary_max:,} below minimum ${prefs.min_salary:,}"

    # ── 6. Location filter ────────────────────────────────────────────────────
    if prefs.preferred_locations and job.location:
        job_loc = normalize_text(job.location)
        location_ok = any(
            normalize_text(loc) in job_loc or job_loc in normalize_text(loc)
            for loc in prefs.preferred_locations
        )
        # Also allow fully remote jobs regardless of location prefs
        is_remote = job.work_mode == WorkMode.remote or "remote" in job_loc
        if not location_ok and not is_remote:
            return False, f"Location '{job.location}' not in preferred locations"

    return True, None
