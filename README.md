# 🚀 Job Application Copilot

> AI-powered job search automation for software engineers — find, score, filter, and tailor applications at scale.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Browser (Next.js 14)                       │
│  Login · Dashboard · Jobs · Tracker · Resume · Preferences    │
│  React Query · Zustand · Tailwind CSS · React Hook Form+Zod   │
└───────────────────────┬──────────────────────────────────────┘
                        │ HTTP REST/JSON
┌───────────────────────▼──────────────────────────────────────┐
│                 FastAPI Backend (Python 3.12)                 │
│  /auth  /resume  /preferences  /jobs  /applications  /dashboard│
│                                                               │
│  Services:                                                    │
│  • Sponsorship Detection  (regex pattern engine)              │
│  • Filter Engine          (exclude keywords, mode, salary)    │
│  • Scoring Engine         (6-factor weighted 0–100)           │
│  • Job Normalizer         (title, salary, skills extraction)  │
│  • Resume Parser          (skills, exp, education)            │
│  • AI Content Service     (Claude API → tailor + cover letter)│
│  • Mock Connector         (15 realistic seed jobs)            │
└───────────────────────┬──────────────────────────────────────┘
                        │ SQLAlchemy ORM
┌───────────────────────▼──────────────────────────────────────┐
│                    PostgreSQL 16                              │
│  users · resumes · user_preferences · jobs · job_scores      │
│  applications                                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Docker 24+ and Docker Compose v2

### 1. Clone

```bash
git clone <repo-url> && cd job-copilot
```

### 2. Launch

```bash
docker compose up --build
```

This automatically:
- Starts PostgreSQL 16
- Creates all database tables
- Seeds demo user + 15 scored mock jobs
- Starts FastAPI on `localhost:8000`
- Starts Next.js on `localhost:3000`

### 3. Open

```
http://localhost:3000
```

**Demo login:** `demo@jobcopilot.dev` / `demo1234`

### 4. Enable AI tailoring (optional)

```bash
# Edit .env:
ANTHROPIC_API_KEY=sk-ant-...
docker compose restart backend
```

Without an API key the app uses a smart mock — all features still work.

---

## Local Dev (no Docker)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://copilot:copilot@localhost:5432/job_copilot
python -c "from app.db.base import Base; from app.db.session import engine; import app.models; Base.metadata.create_all(bind=engine)"
python seed/seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev   # → http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account, returns JWT |
| POST | `/auth/login` | Authenticate, returns JWT |
| GET | `/auth/me` | Current user info |
| POST | `/resume/upload` | Upload + parse resume (multipart) |
| GET | `/resume` | Get active resume |
| GET | `/preferences` | Get user preferences |
| POST | `/preferences` | Create/update preferences |
| GET | `/jobs` | List jobs with scores |
| POST | `/jobs/ingest` | Fetch + score jobs from connectors |
| POST | `/jobs/ingest/manual` | Manually submit a job posting |
| POST | `/jobs/:id/score` | Re-score a single job |
| POST | `/jobs/:id/tailor` | AI-tailor resume + cover letter |
| GET | `/applications` | List applications |
| POST | `/applications` | Save a job as application |
| PATCH | `/applications/:id` | Update status/notes |
| GET | `/dashboard` | Stats + top matches |

Interactive API docs: `http://localhost:8000/docs`

---

## Scoring Engine

| Factor | Weight | Signal |
|--------|--------|--------|
| Title relevance | 25% | Word overlap between job title and target roles |
| Skills match | 25% | Resume skills vs job-required skills |
| Sponsorship compat | 20% | 1.0=available, 0.5=unknown, 0.0=not available |
| Employment type | 10% | Match to preferred types |
| Location fit | 10% | String match; remote jobs always score high |
| Experience level | 10% | Match to preferred levels |

Keyword boost: +2% per matched include keyword (max +10%)

---

## Sponsorship Detection

**Positive signals (boost):** H1B sponsorship, visa sponsorship available, H1B transfer ok, immigration support, open to all work authorizations

**Negative signals (exclude):** no sponsorship, will not sponsor, US citizens only, security clearance required, TS/SCI, must work without sponsorship, cannot sponsor

---

## Database Schema Summary

```
users              → id, email, hashed_password, full_name
resumes            → id, user_id, raw_text, parsed_data (JSONB)
user_preferences   → id, user_id, target_roles, filters, salary, keywords (JSONB arrays)
jobs               → id, title, company, description, sponsorship_status, skills_required
job_scores         → id, job_id, user_id, total_score, factor breakdown, is_filtered_out
applications       → id, user_id, job_id, status, tailored_resume, cover_letter, notes
```

---

## Extending

### Add a real job connector

```python
# backend/app/connectors/remotive_connector.py
import httpx

async def fetch_remotive_jobs(query="python"):
    async with httpx.AsyncClient() as client:
        r = await client.get("https://remotive.com/api/remote-jobs", params={"search": query})
    return [
        {"id": str(j["id"]), "source": "remotive",
         "title": j["title"], "company": j["company_name"],
         "description": j.get("description",""), "url": j.get("url","")}
        for j in r.json().get("jobs", [])
    ]
```

Then call it alongside `fetch_mock_jobs()` in the `/jobs/ingest` route.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| State | Zustand + React Query |
| Forms | React Hook Form + Zod |
| Backend | FastAPI, Python 3.12 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Auth | JWT + bcrypt |
| AI | Anthropic Claude API |
| Container | Docker + Docker Compose |
