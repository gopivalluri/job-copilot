"""
Authentication API routes
POST /auth/register - create account
POST /auth/login    - get JWT token
GET  /auth/me       - current user info
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User, UserPreferences
from app.schemas.schemas import UserCreate, UserLogin, UserOut, Token
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, get_current_user
)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.flush()  # get user.id

    # Create default preferences
    prefs = UserPreferences(
        user_id=user.id,
        target_roles=["Software Engineer", "Backend Engineer", "Python Developer"],
        employment_types=["full_time", "contract"],
        work_modes=["remote", "hybrid"],
        preferred_locations=["Remote"],
        min_salary=90000,
        requires_sponsorship=False,
        exclude_keywords=["clearance required", "US citizens only", "no sponsorship"],
    )
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user."""
    return current_user
