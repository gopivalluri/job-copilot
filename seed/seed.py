#!/usr/bin/env python3
"""
Seed script: creates default demo user + ingests mock jobs + scores them.
Run inside the backend container: python seed/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.models import User, UserPreferences, Resume, Job, JobScore
from app.core.security import get_password_hash
from app.connectors.mock_connector import fetch_mock_jobs
from app.services.normalizer import normalize_job
from app.services.scoring_engine import score_job

DEMO_EMAIL    = "demo@jobcopilot.dev"
DEMO_PASSWORD = "demo1234"
DEMO_NAME     = "Alex Chen"

DEMO_RESUME_TEXT = """Alex Chen
alex.chen@email.com | (512) 555-0192 | Austin, TX
linkedin.com/in/alexchen | github.com/alexchen

SUMMARY
Senior Backend Engineer with 6 years of experience building high-throughput distributed systems
and APIs. Expert in Python, PostgreSQL, and AWS. Passionate about clean architecture,
developer tooling, and performance optimization.

EXPERIENCE

Senior Software Engineer — DataFlow Inc.                         Jan 2021 – Present
• Designed and owned Python/FastAPI microservices processing 5M+ events/day
• Led migration from monolith to microservices, reducing deployment time by 70%
• Built real-time streaming pipeline using Kafka + PostgreSQL handling peak 50k req/sec
• Mentored 4 junior engineers; led weekly architecture review sessions
• Tech: Python, FastAPI, PostgreSQL, Redis, Kafka, Docker, Kubernetes, AWS ECS

Software Engineer — CloudBase Solutions                          Jun 2018 – Dec 2020
• Built RESTful APIs consumed by 200+ enterprise clients
• Optimized critical SQL queries reducing avg response time from 800ms to 40ms
• Implemented CI/CD pipelines with GitHub Actions saving 10 hours/week
• Tech: Python, Django, MySQL, Celery, AWS (EC2, RDS, S3)

SKILLS
Languages: Python (expert), TypeScript, SQL, Bash, Go (learning)
Frameworks: FastAPI, Django, Flask, React
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
Cloud/Infra: AWS (EC2, ECS, RDS, S3, Lambda), Docker, Kubernetes, Terraform
Other: Kafka, Celery, GraphQL, REST, gRPC, Agile/Scrum, Git

EDUCATION
B.S. Computer Science — University of Texas at Austin            2018
"""


def seed():
    print("🌱 Seeding database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Demo user ──────────────────────────────────────────────────────────
        existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if existing:
            print(f"  ✓ User already exists: {DEMO_EMAIL}")
            user = existing
        else:
            user = User(
                email=DEMO_EMAIL,
                hashed_password=get_password_hash(DEMO_PASSWORD),
                full_name=DEMO_NAME,
                is_active=True,
            )
            db.add(user)
            db.flush()
            print(f"  ✓ Created user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ── Preferences ────────────────────────────────────────────────────────
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        if not prefs:
            prefs = UserPreferences(
                user_id=user.id,
                target_roles=["Software Engineer", "Backend Engineer", "Senior Software Engineer",
                               "Python Developer", "Senior Python Engineer"],
                employment_types=["full_time", "contract"],
                work_modes=["remote", "hybrid"],
                preferred_locations=["Texas", "California", "Remote", "Austin", "San Francisco"],
                min_salary=90000,
                requires_sponsorship=True,
                sponsorship_types=["H1B", "H1B_transfer"],
                experience_levels=["mid", "senior", "staff"],
                include_keywords=["python", "fastapi", "postgresql", "aws", "microservices"],
                exclude_keywords=["no sponsorship", "us citizens only", "clearance required",
                                   "must work without sponsorship", "security clearance"],
                auto_score_threshold=70,
                daily_limit=50,
            )
            db.add(prefs)
            db.flush()
            print("  ✓ Created preferences")
        else:
            print("  ✓ Preferences already exist")

        # ── Resume ─────────────────────────────────────────────────────────────
        resume = db.query(Resume).filter(
            Resume.user_id == user.id, Resume.is_active == True
        ).first()
        if not resume:
            from app.services.resume_parser import parse_resume_text
            parsed = parse_resume_text(DEMO_RESUME_TEXT)
            resume = Resume(
                user_id=user.id,
                filename="alex_chen_resume.txt",
                file_path="",
                raw_text=DEMO_RESUME_TEXT,
                parsed_data=parsed,
                is_active=True,
            )
            db.add(resume)
            db.flush()
            print(f"  ✓ Created resume (skills: {parsed['skills'][:5]}...)")
        else:
            print("  ✓ Resume already exists")

        # ── Jobs ───────────────────────────────────────────────────────────────
        raw_jobs = fetch_mock_jobs(limit=50)
        new_jobs = 0
        scored = 0

        for raw in raw_jobs:
            normalized = normalize_job(raw)
            existing_job = db.query(Job).filter(
                Job.source == normalized["source"],
                Job.external_id == normalized["external_id"],
            ).first()

            if existing_job:
                job = existing_job
            else:
                job = Job(**{k: v for k, v in normalized.items() if hasattr(Job, k)})
                db.add(job)
                db.flush()
                new_jobs += 1

            # Score against demo user
            sc = db.query(JobScore).filter(
                JobScore.job_id == job.id, JobScore.user_id == user.id
            ).first()
            if not sc:
                total, factors, filtered, reason = score_job(job, prefs, resume)
                sc = JobScore(
                    job_id=job.id,
                    user_id=user.id,
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
                db.add(sc)
                scored += 1

        db.commit()
        print(f"  ✓ Ingested {new_jobs} new jobs, scored {scored}")
        print("\n✅ Seed complete!")
        print(f"\n  Login: {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
