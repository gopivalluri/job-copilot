"""
Match Scoring Engine
Computes a composite 0-100 score for a job against user preferences + resume.
Factors:
  - Title relevance       (25%)
  - Skills match          (25%)
  - Sponsorship compat    (20%)
  - Employment type       (10%)
  - Location fit          (10%)
  - Experience level      (10%)
"""
from typing import Dict, List, Optional, Tuple
import re

from app.models.models import (
    Job, UserPreferences, Resume,
    SponsorshipStatus, WorkMode, EmploymentType, ExperienceLevel
)
from app.services.sponsorship_engine import sponsorship_score_for_user
from app.services.filter_engine import job_passes_filters


# ─── Weights ──────────────────────────────────────────────────────────────────
WEIGHTS = {
    "title":       0.25,
    "skills":      0.25,
    "sponsorship": 0.20,
    "employment":  0.10,
    "location":    0.10,
    "experience":  0.10,
}


def _normalize(text: str) -> str:
    return text.lower().strip() if text else ""


def _title_relevance_score(job_title: str, target_roles: List[str]) -> float:
    """Score how well job title matches any target role (0-1)."""
    if not target_roles:
        return 0.6  # neutral

    job_title_lower = _normalize(job_title)
    best = 0.0

    for role in target_roles:
        role_lower = _normalize(role)
        role_words = set(role_lower.split())
        title_words = set(job_title_lower.split())

        # Exact match
        if role_lower == job_title_lower:
            return 1.0

        # Role is substring of title
        if role_lower in job_title_lower:
            best = max(best, 0.9)
            continue

        # Word overlap (Jaccard-like)
        overlap = role_words & title_words
        if overlap:
            score = len(overlap) / len(role_words | title_words)
            best = max(best, min(0.85, score * 1.5))  # boost overlap

    return best


def _skills_match_score(
    job_skills: List[str],
    resume_skills: List[str],
    job_description: str = "",
) -> float:
    """Ratio of job-required skills found in resume (0-1)."""
    if not resume_skills:
        return 0.5  # no resume data: neutral

    resume_set = {_normalize(s) for s in resume_skills}
    job_set = {_normalize(s) for s in job_skills}

    # Also check description for skills keywords if job_skills is sparse
    if len(job_set) < 3 and job_description:
        # Extract common tech keywords from description
        tech_keywords = re.findall(
            r'\b(python|java|javascript|typescript|react|node|sql|postgres|docker|'
            r'kubernetes|aws|gcp|azure|fastapi|django|flask|spring|kafka|redis|'
            r'mongodb|graphql|rest|api|microservice|ci/cd|terraform|git)\b',
            job_description.lower()
        )
        job_set |= set(tech_keywords)

    if not job_set:
        return 0.5

    matches = resume_set & job_set
    return len(matches) / len(job_set)


def _employment_type_score(
    job_type: Optional[EmploymentType],
    preferred_types: List[str]
) -> float:
    if not preferred_types or job_type is None:
        return 0.6  # neutral
    return 1.0 if job_type.value in [t.lower() for t in preferred_types] else 0.2


def _location_score(
    job: Job,
    preferred_locations: List[str],
    preferred_modes: List[str]
) -> float:
    # Remote job: high score if remote is preferred
    if job.work_mode == WorkMode.remote:
        return 1.0 if "remote" in [m.lower() for m in preferred_modes] else 0.7

    if not preferred_locations:
        return 0.5

    job_loc = _normalize(job.location or "")
    for loc in preferred_locations:
        if _normalize(loc) in job_loc or job_loc in _normalize(loc):
            return 1.0

    return 0.2


def _experience_level_score(
    job_level: Optional[ExperienceLevel],
    preferred_levels: List[str]
) -> float:
    if not preferred_levels or job_level is None:
        return 0.6  # neutral
    return 1.0 if job_level.value in [l.lower() for l in preferred_levels] else 0.4


# ─── Main scoring function ────────────────────────────────────────────────────

def score_job(
    job: Job,
    prefs: UserPreferences,
    resume: Optional[Resume] = None,
) -> Tuple[float, Dict[str, float], bool, Optional[str]]:
    """
    Returns (total_score, factor_scores, is_filtered_out, filter_reason).
    total_score is 0-100.
    """
    # First check hard filters
    passes, filter_reason = job_passes_filters(job, prefs)
    is_filtered_out = not passes

    # Get resume skills
    resume_skills: List[str] = []
    if resume and resume.parsed_data:
        resume_skills = resume.parsed_data.get("skills", [])

    # Compute individual factor scores (0-1)
    title_s = _title_relevance_score(job.title, prefs.target_roles or [])
    skills_s = _skills_match_score(
        job.skills_required or [],
        resume_skills,
        job.description or ""
    )
    sponsorship_s = sponsorship_score_for_user(
        job.sponsorship_status or SponsorshipStatus.unknown,
        prefs.requires_sponsorship
    )
    employment_s = _employment_type_score(job.employment_type, prefs.employment_types or [])
    location_s = _location_score(job, prefs.preferred_locations or [], prefs.work_modes or [])
    experience_s = _experience_level_score(job.experience_level, prefs.experience_levels or [])

    # Weighted composite
    raw = (
        title_s       * WEIGHTS["title"]       +
        skills_s      * WEIGHTS["skills"]      +
        sponsorship_s * WEIGHTS["sponsorship"] +
        employment_s  * WEIGHTS["employment"]  +
        location_s    * WEIGHTS["location"]    +
        experience_s  * WEIGHTS["experience"]
    )

    # Boost for include keywords
    description_text = (job.description or "").lower()
    include_boost = 0.0
    for kw in (prefs.include_keywords or []):
        if kw.lower() in description_text:
            include_boost += 0.02  # 2% per match, max ~10%

    total = min(100.0, round((raw + min(include_boost, 0.10)) * 100, 1))

    # Filtered-out jobs get score capped at 0
    if is_filtered_out:
        total = 0.0

    factor_scores = {
        "title_score":       round(title_s * 100, 1),
        "skills_score":      round(skills_s * 100, 1),
        "sponsorship_score": round(sponsorship_s * 100, 1),
        "employment_score":  round(employment_s * 100, 1),
        "location_score":    round(location_s * 100, 1),
        "experience_score":  round(experience_s * 100, 1),
    }

    return total, factor_scores, is_filtered_out, filter_reason
