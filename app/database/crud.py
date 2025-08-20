from sqlalchemy.orm import Session
from app.database import models

def get_user(db: Session, telegram_id: int):
    """Получаем пользователя по telegram_id"""
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int, username: str = None, language: str = 'ru'):
    """Создаем нового пользователя с указанным языком (по умолчанию русский)"""
    db_user = models.User(
        telegram_id=telegram_id,
        username=username,
        language=language  # Устанавливаем язык при создании
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_language(db: Session, telegram_id: int, language: str):
    """Обновляем язык пользователя"""
    user = get_user(db, telegram_id)
    if not user:
        # Если пользователя нет - создаем с выбранным языком
        return create_user(db, telegram_id, language=language)
    
    user.language = language
    db.commit()
    db.refresh(user)
    return user

def get_user_language(db: Session, telegram_id: int) -> str:
    """Получаем текущий язык пользователя"""
    user = get_user(db, telegram_id)
    return user.language if user else 'ru'  # По умолчанию русский