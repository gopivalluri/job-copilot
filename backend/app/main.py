"""
Job Application Copilot - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.routes import auth, resume, preferences, jobs, applications, dashboard
from app.db.session import engine
from app.models import models  # noqa: F401 - ensure models are imported for table creation

app = FastAPI(
    title="Job Application Copilot API",
    description="Smart job search automation for software engineers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router,        prefix="/auth",         tags=["auth"])
app.include_router(resume.router,      prefix="/resume",       tags=["resume"])
app.include_router(preferences.router, prefix="/preferences",  tags=["preferences"])
app.include_router(jobs.router,        prefix="/jobs",         tags=["jobs"])
app.include_router(applications.router,prefix="/applications", tags=["applications"])
app.include_router(dashboard.router,   prefix="/dashboard",    tags=["dashboard"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
