from sqlalchemy.orm import Session
from app.database.models import User, DepositHistory, CrashBetHistory
from typing import Optional

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Получаем пользователя по telegram_id"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(
    db: Session, 
    telegram_id: int, 
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    referrer_id: Optional[int] = None,
    language: str = 'ru',  # Добавляем язык по умолчанию
    photo_url: str = None 
) -> User:
    """Создаем нового пользователя с учетом реферальной системы"""
    db_user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        referrer_id=referrer_id,
        language=language,
        photo_url=photo_url # Устанавливаем язык
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Если есть реферер, обновляем его счетчики
    if referrer_id:
        update_referrer_stats(db, referrer_id)
    
    return db_user

def update_user_language(db: Session, telegram_id: int, language: str):
    """Обновляем язык пользователя"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        # Если пользователя нет - создаем с выбранным языком
        return create_user(db, telegram_id, language=language)
    
    user.language = language
    db.commit()
    db.refresh(user)
    return user

def update_referrer_stats(db: Session, referrer_id: int):
    """Обновляем статистику реферера"""
    referrer = db.query(User).filter(User.id == referrer_id).first()
    if referrer:
        referrer.referrals_count = db.query(User).filter(
            User.referrer_id == referrer_id
        ).count()
        referrer.active_referrals = db.query(User).filter(
            User.referrer_id == referrer_id,
            User.ton_balance > 0  # или другая логика активности
        ).count()
        db.commit()

def update_user_balance(
    db: Session, 
    telegram_id: int, 
    currency: str, 
    amount: float
) -> Optional[User]:
    """Обновляем баланс пользователя"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return None
    
    if currency == 'ton':
        user.ton_balance += amount
    elif currency == 'stars':
        user.stars_balance += amount
    
    db.commit()
    db.refresh(user)
    return user

def get_user_balance(db: Session, telegram_id: int) -> dict:
    """Получаем балансы пользователя"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return {'ton': 0.0, 'stars': 0.0}
    
    return {'ton': user.ton_balance, 'stars': user.stars_balance}

def add_deposit_history(
    db: Session,
    user_id: int,
    telegram_id: int,
    amount: float,
    note: Optional[str] = None
) -> DepositHistory:
    """Добавляем запись в историю депозитов"""
    deposit = DepositHistory(
        user_id=user_id,
        telegram_id=telegram_id,
        amount=amount,
        note=note
    )
    
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return deposit

def add_crash_bet(
    db: Session,
    user_id: int,
    telegram_id: int,
    bet_amount: float,
    crash_coefficient: Optional[float] = None,
    win_amount: float = 0.0,
    status: str = 'pending'
) -> CrashBetHistory:
    """Добавляем запись о ставке в crash игру"""
    # Получаем последний номер ставки для пользователя
    last_bet = db.query(CrashBetHistory).filter(
        CrashBetHistory.user_id == user_id
    ).order_by(CrashBetHistory.bet_number.desc()).first()
    
    next_bet_number = (last_bet.bet_number + 1) if last_bet else 1
    
    bet = CrashBetHistory(
        user_id=user_id,
        telegram_id=telegram_id,
        bet_number=next_bet_number,
        bet_amount=bet_amount,
        crash_coefficient=crash_coefficient,
        win_amount=win_amount,
        status=status
    )
    
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet

get_user = get_user_by_telegram_id