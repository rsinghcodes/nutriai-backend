from fastapi import APIRouter, Request, Depends
from db.models.user import User
from schemas.user import UserResponse
from sqlalchemy.orm import Session
from db.session import get_db

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_me(request: Request, db: Session = Depends(get_db)):
    current_user: User = request.state.user
    return current_user
