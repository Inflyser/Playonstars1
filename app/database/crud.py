from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import models
from app.database.models import User, DepositHistory, CrashBetHistory, Wallet, Transaction, CrashGameResult, AdminUser
from typing import Optional
from typing import List

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получаем пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()

def add_stars_payment_id(db: Session, telegram_id: int, payment_id: str) -> bool:
    """Добавляем ID платежа в историю пользователя"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return False
    
    if user.stars_payment_ids is None:
        user.stars_payment_ids = []
    
    # Проверяем не добавляли ли уже этот ID
    if payment_id not in user.stars_payment_ids:
        user.stars_payment_ids.append(payment_id)
        db.commit()
        return True
    
    return False




def has_stars_payment_id(db: Session, telegram_id: int, payment_id: str) -> bool:
    """Проверяем есть ли уже такой ID платежа"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user or not user.stars_payment_ids:
        return False
    
    return payment_id in user.stars_payment_ids
def create_user(
    db: Session, 
    telegram_id: int, 
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    referrer_id: Optional[int] = None,
    language: str = 'ru',
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
        photo_url=photo_url
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
            User.ton_balance > 0
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


def get_user_crash_bet_history(db: Session, user_id: int, limit: int = 50):
    """Получаем историю ставок пользователя"""
    return db.query(CrashBetHistory).filter(
        CrashBetHistory.user_id == user_id
    ).order_by(
        CrashBetHistory.created_at.desc()
    ).limit(limit).all()

def get_all_crash_bet_history(db: Session, limit: int = 100):
    """Получаем всю историю ставок"""
    return db.query(CrashBetHistory).order_by(
        CrashBetHistory.created_at.desc()
    ).limit(limit).all()

def get_crash_bet_by_id(db: Session, bet_id: int):
    """Получаем ставку по ID"""
    return db.query(CrashBetHistory).filter(CrashBetHistory.id == bet_id).first()

def get_user_active_crash_bets(db: Session, user_id: int):
    """Получаем активные ставки пользователя"""
    return db.query(CrashBetHistory).filter(
        CrashBetHistory.user_id == user_id,
        CrashBetHistory.status == 'pending'
    ).all()

def get_wallet_by_address(db: Session, address: str):
    return db.query(Wallet).filter(Wallet.address == address).first()

def get_pending_transactions(db: Session, user_id: int):
    """Получаем pending транзакции пользователя"""
    return db.query(Transaction).filter(
        Transaction.wallet_id.in_(
            db.query(Wallet.id).filter(Wallet.user_id == user_id)
        ),
        Transaction.status == "pending"
    ).all()

def get_wallet_by_user(db: Session, user_id: int):
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()

def create_wallet(db: Session, user_id: int, address: str, wallet_provider: str = "tonconnect"):
    db_wallet = Wallet(
        user_id=user_id,
        address=address,
        wallet_provider=wallet_provider
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def create_transaction(db: Session, wallet_id: int, tx_hash: str, amount: float, transaction_type: str):
    db_transaction = Transaction(
        wallet_id=wallet_id,
        tx_hash=tx_hash,
        amount=amount,
        transaction_type=transaction_type
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction_by_hash(db: Session, tx_hash: str):
    return db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()

def update_transaction_status(db: Session, tx_hash: str, status: str):
    db_transaction = get_transaction_by_hash(db, tx_hash)
    if db_transaction:
        db_transaction.status = status
        if status == "completed":
            db_transaction.completed_at = func.now()
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def get_user_wallets(db: Session, user_id: int):
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()

def create_crash_game_result(db: Session, game_id: int, multiplier: float, crashed_at: float, 
                           total_players: int = 0, total_bet: float = 0.0, total_payout: float = 0.0):
    """Создаем запись о результате краш-игры"""
    db_result = CrashGameResult(
        game_id=game_id,
        multiplier=multiplier,
        crashed_at=crashed_at,
        total_players=total_players,
        total_bet=total_bet,
        total_payout=total_payout
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def update_crash_bet_result(db: Session, bet_id: int, crash_coefficient: float, 
                          win_amount: float, status: str):
    """Обновляем результат ставки в краш-игре"""
    bet = db.query(CrashBetHistory).filter(CrashBetHistory.id == bet_id).first()
    if bet:
        bet.crash_coefficient = crash_coefficient
        bet.win_amount = win_amount
        bet.status = status
        bet.ended_at = func.now()
        db.commit()
        db.refresh(bet)
    return bet

def get_user_active_crash_bets(db: Session, user_id: int):
    """Получаем активные ставки пользователя в краш-игре"""
    return db.query(CrashBetHistory).filter(
        CrashBetHistory.user_id == user_id,
        CrashBetHistory.status == 'pending'
    ).all()

def get_crash_game_history(db: Session, limit: int = 50):
    """Получаем историю краш-игр"""
    return db.query(CrashGameResult).order_by(
        CrashGameResult.timestamp.desc()
    ).limit(limit).all()

get_user = get_user_by_telegram_id


def add_stars_payment_id(db: Session, telegram_id: int, payment_id: str) -> bool:
    """Добавляем ID платежа в историю пользователя"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return False
    
    if user.stars_payment_ids is None:
        user.stars_payment_ids = []
    
    # Проверяем не добавляли ли уже этот ID
    if payment_id not in user.stars_payment_ids:
        user.stars_payment_ids.append(payment_id)
        db.commit()
        return True
    
    return False

def has_stars_payment_id(db: Session, telegram_id: int, payment_id: str) -> bool:
    """Проверяем есть ли уже такой ID платежа"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user or not user.stars_payment_ids:
        return False
    
    return payment_id in user.stars_payment_ids


def get_game_settings(db: Session):
    """Получаем настройки игры"""
    from app.database.models import GameSettings
    
    settings = db.query(GameSettings).first()
    if not settings:
        # Если настроек нет - создаем по умолчанию
        return init_default_settings(db)
    return settings

def update_game_settings(
    db: Session,
    admin_password: str = None,
    crash_rtp: float = None,
    crash_min_multiplier: float = None,
    crash_max_multiplier: float = None
):
    """Обновляем настройки игры"""
    from app.database.models import GameSettings
    
    settings = db.query(GameSettings).first()
    
    if not settings:
        # Создаем новые настройки если их нет
        settings = GameSettings()
        db.add(settings)
    
    if admin_password is not None:
        settings.admin_password = admin_password
    if crash_rtp is not None:
        settings.crash_rtp = crash_rtp
    if crash_min_multiplier is not None:
        settings.crash_min_multiplier = crash_min_multiplier
    if crash_max_multiplier is not None:
        settings.crash_max_multiplier = crash_max_multiplier
    
    db.commit()
    db.refresh(settings)
    return settings


def init_default_settings(db: Session):
    """Создает настройки по умолчанию при первом запуске"""
    from app.database.models import GameSettings
    
    # Проверяем есть ли уже настройки
    existing_settings = db.query(GameSettings).first()
    if not existing_settings:
        # Создаем настройки по умолчанию
        default_settings = GameSettings(
            admin_password="KBV4B92clwn8juHJHF45106KBNJHF31cvo2pl5g",  # Пароль по умолчанию
            crash_rtp=0.95,
            crash_min_multiplier=1.1,
            crash_max_multiplier=100.0
        )
        db.add(default_settings)
        db.commit()
        db.refresh(default_settings)
        print("✅ Настройки по умолчанию созданы")
        print("🔐 Пароль админа по умолчанию: admin")
    return existing_settings


def is_user_admin(db: Session, telegram_id: int) -> bool:
    """Проверяем является ли пользователь админом"""
    from app.database.models import AdminUser
    admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    return admin is not None

def add_admin_user(db: Session, telegram_id: int, username: str = None) -> AdminUser:
    """Добавляем пользователя в админы"""
    from app.database.models import AdminUser
    
    # Проверяем нет ли уже такого админа
    existing_admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    if existing_admin:
        return existing_admin
    
    # Создаем нового админа
    admin = AdminUser(telegram_id=telegram_id, username=username)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def remove_admin_user(db: Session, telegram_id: int) -> bool:
    """Удаляем пользователя из админов"""
    from app.database.models import AdminUser
    
    admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    if admin:
        db.delete(admin)
        db.commit()
        return True
    return False

def get_all_admins(db: Session) -> List[AdminUser]:
    """Получаем всех админов"""
    from app.database.models import AdminUser
    return db.query(AdminUser).all()