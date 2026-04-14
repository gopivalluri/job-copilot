"""
Jobs API routes
GET  /jobs                - list jobs with scores
POST /jobs/ingest         - trigger ingestion from connectors
POST /jobs/ingest/manual  - manually submit a job
GET  /jobs/:id            - job detail
POST /jobs/:id/score      - score a job against current user
POST /jobs/:id/tailor     - AI-tailor resume for a job
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Job, JobScore, Resume, User, UserPreferences
from app.schemas.schemas import JobOut, JobWithScore, JobIngest, ScoreOut, TailorRequest, TailorResponse
from app.services.normalizer import normalize_job
from app.services.scoring_engine import score_job
from app.services.ai_service import generate_tailored_content
from app.connectors.mock_connector import fetch_mock_jobs

router = APIRouter()


def _get_score_for_user(job: Job, user_id: int, db: Session) -> Optional[JobScore]:
    return db.query(JobScore).filter(
        JobScore.job_id == job.id, JobScore.user_id == user_id
    ).first()


def _attach_score(job: Job, score_obj: Optional[JobScore]) -> JobWithScore:
    j = JobWithScore.model_validate(job)
    if score_obj:
        j.score = score_obj.total_score
        j.score_details = {
            "title":       score_obj.title_score,
            "skills":      score_obj.skills_score,
            "sponsorship": score_obj.sponsorship_score,
            "employment":  score_obj.employment_score,
            "location":    score_obj.location_score,
            "experience":  score_obj.experience_score,
        }
        j.is_filtered_out = score_obj.is_filtered_out
        j.filter_reason = score_obj.filter_reason
    return j


@router.get("", response_model=List[JobWithScore])
def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    min_score: Optional[float] = Query(default=None),
    include_filtered: bool = Query(default=False),
    work_mode: Optional[str] = Query(default=None),
    sponsorship_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all jobs with user-specific scores. Sorted by score desc."""
    query = db.query(Job).filter(Job.is_active == True)

    if work_mode:
        query = query.filter(Job.work_mode == work_mode)

    if sponsorship_only:
        from app.models.models import SponsorshipStatus
        query = query.filter(Job.sponsorship_status.in_([
            SponsorshipStatus.available, SponsorshipStatus.transfer_ok
        ]))

    jobs = query.order_by(Job.ingested_at.desc()).offset(skip).limit(limit).all()

    result = []
    for job in jobs:
        score_obj = _get_score_for_user(job, current_user.id, db)
        jws = _attach_score(job, score_obj)

        if not include_filtered and jws.is_filtered_out:
            continue
        if min_score is not None and (jws.score or 0) < min_score:
            continue

        result.append(jws)

    # Sort by score descending
    result.sort(key=lambda x: x.score or 0, reverse=True)
    return result


@router.get("/{job_id}", response_model=JobWithScore)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    score_obj = _get_score_for_user(job, current_user.id, db)
    return _attach_score(job, score_obj)


@router.post("/ingest", status_code=status.HTTP_200_OK)
def ingest_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch jobs from all connectors, normalize, persist, and score them."""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id, Resume.is_active == True
    ).first()

    raw_jobs = fetch_mock_jobs(limit=50)

    new_count = 0
    scored_count = 0

    for raw in raw_jobs:
        normalized = normalize_job(raw)

        # Upsert job
        existing = db.query(Job).filter(
            Job.source == normalized["source"],
            Job.external_id == normalized["external_id"]
        ).first()

        if existing:
            job = existing
        else:
            job = Job(**{k: v for k, v in normalized.items() if hasattr(Job, k)})
            db.add(job)
            try:
                db.flush()
                new_count += 1
            except IntegrityError:
                db.rollback()
                continue

        # Score against current user if prefs exist
        if prefs:
            total, factors, filtered, reason = score_job(job, prefs, resume)

            score_obj = db.query(JobScore).filter(
                JobScore.job_id == job.id, JobScore.user_id == current_user.id
            ).first()

            if score_obj:
                score_obj.total_score = total
                score_obj.title_score = factors["title_score"]
                score_obj.skills_score = factors["skills_score"]
                score_obj.sponsorship_score = factors["sponsorship_score"]
                score_obj.employment_score = factors["employment_score"]
                score_obj.location_score = factors["location_score"]
                score_obj.experience_score = factors["experience_score"]
                score_obj.is_filtered_out = filtered
                score_obj.filter_reason = reason
            else:
                score_obj = JobScore(
                    job_id=job.id,
                    user_id=current_user.id,
                    total_score=total,
                    title_score=factors["title_score"],
                    skills_score=factors["skills_score"],
                    sponsorship_score=factors["sponsorship_score"],
                    employment_score=factors["employment_score"],
                    location_score=factors["location_score"],
                    experience_score=factors["experience_score"],
                    is_filtered_out=filtered,
                    filter_reason=reason,
                )
                db.add(score_obj)
            scored_count += 1

    db.commit()

    return {
        "message": f"Ingestion complete",
        "new_jobs": new_count,
        "total_fetched": len(raw_jobs),
        "scored": scored_count,
    }


@router.post("/ingest/manual", response_model=JobWithScore, status_code=status.HTTP_201_CREATED)
def ingest_manual_job(
    payload: JobIngest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually submit a job posting URL or paste for ingestion."""
    import uuid as _uuid
    raw = payload.model_dump()
    raw["id"] = f"manual-{_uuid.uuid4().hex[:8]}"
    raw["source"] = "manual"
    normalized = normalize_job(raw)

    job = Job(**{k: v for k, v in normalized.items() if hasattr(Job, k)})
    db.add(job)
    db.flush()

    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id, Resume.is_active == True
    ).first()

    score_obj = None
    if prefs:
        total, factors, filtered, reason = score_job(job, prefs, resume)
        score_obj = JobScore(
            job_id=job.id,
            user_id=current_user.id,
            total_score=total,
            title_score=factors["title_score"],
            skills_score=factors["skills_score"],
            sponsorship_score=factors["sponsorship_score"],
            employment_score=factors["employment_score"],
            location_score=factors["location_score"],
            experience_score=factors["experience_score"],
            is_filtered_out=filtered,
            filter_reason=reason,
        )
        db.add(score_obj)

    db.commit()
    db.refresh(job)
    return _attach_score(job, score_obj)


@router.post("/{job_id}/score", response_model=ScoreOut)
def score_single_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """(Re)score a specific job against current user preferences."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not prefs:
        raise HTTPException(status_code=400, detail="Set preferences before scoring")

    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id, Resume.is_active == True
    ).first()

    total, factors, filtered, reason = score_job(job, prefs, resume)

    score_obj = db.query(JobScore).filter(
        JobScore.job_id == job_id, JobScore.user_id == current_user.id
    ).first()

    if score_obj:
        score_obj.total_score = total
        score_obj.title_score = factors["title_score"]
        score_obj.skills_score = factors["skills_score"]
        score_obj.sponsorship_score = factors["sponsorship_score"]
        score_obj.employment_score = factors["employment_score"]
        score_obj.location_score = factors["location_score"]
        score_obj.experience_score = factors["experience_score"]
        score_obj.is_filtered_out = filtered
        score_obj.filter_reason = reason
    else:
        score_obj = JobScore(
            job_id=job_id,
            user_id=current_user.id,
            total_score=total,
            title_score=factors["title_score"],
            skills_score=factors["skills_score"],
            sponsorship_score=factors["sponsorship_score"],
            employment_score=factors["employment_score"],
            location_score=factors["location_score"],
            experience_score=factors["experience_score"],
            is_filtered_out=filtered,
            filter_reason=reason,
        )
        db.add(score_obj)

    db.commit()
    db.refresh(score_obj)
    return score_obj


@router.post("/{job_id}/tailor", response_model=TailorResponse)
async def tailor_for_job(
    job_id: int,
    payload: TailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI-tailored resume content and cover letter for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id, Resume.is_active == True
    ).first()
    if not resume or not resume.raw_text:
        raise HTTPException(status_code=400, detail="Upload a resume before tailoring")

    tailored, cover_letter, key_matches, suggestions = await generate_tailored_content(
        resume_text=resume.raw_text,
        job_title=job.title,
        company=job.company,
        job_description=job.description or "",
        generate_cover_letter=payload.generate_cover_letter,
    )

    return TailorResponse(
        tailored_resume=tailored,
        cover_letter=cover_letter,
        key_matches=key_matches,
        suggestions=suggestions,
    )
