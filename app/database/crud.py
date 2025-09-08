from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import models
from app.database.models import User, DepositHistory, CrashBetHistory, Wallet, Transaction, CrashGameResult
from typing import Optional

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Получаем пользователя по telegram_id"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получаем пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()

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
    currency: str,  # ✅ Добавляем параметр валюты
    amount: float
) -> Optional[User]:
    """Обновляем баланс пользователя с указанием валюты"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return None
    
    if currency == 'ton':
        user.ton_balance += amount
    elif currency == 'stars':
        user.stars_balance += amount
    else:
        raise ValueError(f"Unknown currency: {currency}")
    
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
    status: str = 'pending'
) -> CrashBetHistory:
    """Добавляем запись о ставке в crash игру"""
    print(f"🎯 [CRUD] Adding crash bet: user_id={user_id}, amount={bet_amount}")
    
    try:
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
            status=status
        )
        
        db.add(bet)
        db.commit()
        db.refresh(bet)
        
        print(f"✅ [CRUD] Bet saved: ID {bet.id}, Number {bet.bet_number}")
        return bet
        
    except Exception as e:
        print(f"❌ [CRUD] Error adding crash bet: {e}")
        db.rollback()
        raise


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