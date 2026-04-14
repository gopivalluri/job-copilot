"""
Dashboard API route
GET /dashboard - aggregated stats and top matches
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import (
    Application, ApplicationStatus, Job, JobScore,
    SponsorshipStatus, User
)
from app.schemas.schemas import DashboardStats, JobWithScore

router = APIRouter()


@router.get("", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = current_user.id
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Total jobs in DB
    total_jobs = db.query(func.count(Job.id)).scalar() or 0

    # Jobs scored today for this user
    jobs_scored_today = db.query(func.count(JobScore.id)).filter(
        JobScore.user_id == uid,
        JobScore.scored_at >= today_start,
    ).scalar() or 0

    # Applications breakdown by status
    apps = db.query(Application.status, func.count(Application.id)).filter(
        Application.user_id == uid
    ).group_by(Application.status).all()
    apps_by_status = {s.value: c for s, c in apps}
    total_apps = sum(apps_by_status.values())

    # Applied today
    applied_today = db.query(func.count(Application.id)).filter(
        Application.user_id == uid,
        Application.applied_at >= today_start,
    ).scalar() or 0

    # Average match score (non-filtered)
    avg_score = db.query(func.avg(JobScore.total_score)).filter(
        JobScore.user_id == uid,
        JobScore.is_filtered_out == False,
        JobScore.total_score > 0,
    ).scalar() or 0.0

    # Sponsorship-eligible jobs
    sponsorship_eligible = db.query(func.count(Job.id)).filter(
        Job.sponsorship_status.in_([SponsorshipStatus.available, SponsorshipStatus.transfer_ok])
    ).scalar() or 0

    # Top 10 matches
    top_score_rows = (
        db.query(JobScore)
        .filter(
            JobScore.user_id == uid,
            JobScore.is_filtered_out == False,
            JobScore.total_score > 0,
        )
        .order_by(JobScore.total_score.desc())
        .limit(10)
        .all()
    )

    top_matches = []
    for sc in top_score_rows:
        if not sc.job:
            continue
        jws = JobWithScore.model_validate(sc.job)
        jws.score = sc.total_score
        jws.score_details = {
            "title":       sc.title_score,
            "skills":      sc.skills_score,
            "sponsorship": sc.sponsorship_score,
            "employment":  sc.employment_score,
            "location":    sc.location_score,
            "experience":  sc.experience_score,
        }
        jws.is_filtered_out = sc.is_filtered_out
        jws.filter_reason = sc.filter_reason
        top_matches.append(jws)

    return DashboardStats(
        total_jobs_ingested=total_jobs,
        jobs_scored_today=jobs_scored_today,
        top_matches=top_matches,
        applications_by_status=apps_by_status,
        total_applications=total_apps,
        applied_today=applied_today,
        avg_match_score=round(float(avg_score), 1),
        sponsorship_eligible=sponsorship_eligible,
    )
