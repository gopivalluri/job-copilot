"""
Resume API routes
POST /resume/upload   - upload and parse resume
GET  /resume          - get active resume
GET  /resume/all      - list all user resumes
DELETE /resume/:id    - delete a resume
"""
import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Resume, User
from app.schemas.schemas import ResumeOut
from app.services.resume_parser import extract_text_from_upload, parse_resume_text

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a resume file (PDF, DOCX, or TXT) and parse it."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Use PDF, DOCX, or TXT.",
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "resume.txt")[1] or ".txt"
    save_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    with open(save_path, "wb") as f:
        f.write(contents)

    # Parse text
    raw_text = await extract_text_from_upload(save_path, file.content_type or "")
    parsed_data = parse_resume_text(raw_text)

    # Deactivate existing active resumes
    db.query(Resume).filter(
        Resume.user_id == current_user.id, Resume.is_active == True
    ).update({"is_active": False})

    # Save to DB
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=save_path,
        raw_text=raw_text[:50000],  # cap for storage
        parsed_data=parsed_data,
        is_active=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("", response_model=ResumeOut)
def get_active_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current active resume."""
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found. Please upload one.")
    return resume


@router.get("/all", response_model=list[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all resumes for the current user."""
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume."""
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete file from disk
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()
