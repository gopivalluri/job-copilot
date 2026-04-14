"""
Applications API routes - track job applications
GET    /applications         - list all applications
POST   /applications         - create/save an application
GET    /applications/:id     - get detail
PATCH  /applications/:id     - update status / notes
DELETE /applications/:id     - remove
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Application, ApplicationStatus, Job, User
from app.schemas.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter()


@router.get("", response_model=List[ApplicationOut])
def list_applications(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.last_updated.desc())
    )
    if status_filter:
        try:
            status_enum = ApplicationStatus(status_filter)
            query = query.filter(Application.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    apps = query.all()
    result = []
    for app in apps:
        a = ApplicationOut.model_validate(app)
        if app.job:
            from app.schemas.schemas import JobOut
            a.job = JobOut.model_validate(app.job)
        result.append(a)
    return result


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check for duplicate
    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == payload.job_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Application already exists for this job")

    app = Application(
        user_id=current_user.id,
        job_id=payload.job_id,
        notes=payload.notes,
        status=ApplicationStatus.saved,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    result = ApplicationOut.model_validate(app)
    if app.job:
        from app.schemas.schemas import JobOut
        result.job = JobOut.model_validate(app.job)
    return result


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    result = ApplicationOut.model_validate(app)
    if app.job:
        from app.schemas.schemas import JobOut
        result.job = JobOut.model_validate(app.job)
    return result


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Auto-set applied_at when status transitions to "applied"
    if update_data.get("status") == ApplicationStatus.applied and not app.applied_at:
        app.applied_at = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(app, field, value)

    db.commit()
    db.refresh(app)

    result = ApplicationOut.model_validate(app)
    if app.job:
        from app.schemas.schemas import JobOut
        result.job = JobOut.model_validate(app.job)
    return result


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == current_user.id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
