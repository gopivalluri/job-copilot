from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")

async def run_daily_fetch():
    from app.db.session import SessionLocal
    from app.models.models import User, UserPreferences, Resume, Job, JobScore
    from app.connectors.remotive_connector import fetch_remotive_jobs
    from app.connectors.mock_connector import fetch_mock_jobs
    from app.services.normalizer import normalize_job
    from app.services.scoring_engine import score_job
    from sqlalchemy.exc import IntegrityError
    db = SessionLocal()
    try:
        remotive = await fetch_remotive_jobs(limit=50)
        mock = fetch_mock_jobs(limit=15)
        new_count = 0
        new_jobs = []
        for raw in remotive + mock:
            n = normalize_job(raw)
            if not db.query(Job).filter(Job.source==n["source"],Job.external_id==n["external_id"]).first():
                job = Job(**{k:v for k,v in n.items() if hasattr(Job,k)})
                db.add(job)
                try:
                    db.flush(); new_count += 1; new_jobs.append(job)
                except IntegrityError: db.rollback()
        db.commit()
        logger.info(f"Daily fetch: {new_count} new jobs")
        for user in db.query(User).filter(User.is_active==True).all():
            prefs = db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
            resume = db.query(Resume).filter(Resume.user_id==user.id,Resume.is_active==True).first()
            if not prefs: continue
            for job in new_jobs:
                total,factors,filtered,reason = score_job(job,prefs,resume)
                db.add(JobScore(job_id=job.id,user_id=user.id,total_score=total,title_score=factors["title_score"],skills_score=factors["skills_score"],sponsorship_score=factors["sponsorship_score"],employment_score=factors["employment_score"],location_score=factors["location_score"],experience_score=factors["experience_score"],is_filtered_out=filtered,filter_reason=reason))
        db.commit()
    except Exception as e:
        logger.error(f"Daily fetch error: {e}"); db.rollback()
    finally: db.close()

def start_scheduler():
    scheduler.add_job(run_daily_fetch,trigger=CronTrigger(hour=8,minute=0),id="daily_job_fetch",replace_existing=True)
    scheduler.start()
    logger.info("Daily scheduler started (8am UTC)")
