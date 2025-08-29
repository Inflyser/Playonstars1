from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получаем текущего пользователя из сессии"""
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user