from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, ForeignKey, Index, func, Boolean, Numeric
from sqlalchemy.orm import relationship, backref 
from app.database.session import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    wallet_provider = Column(String, default="tonconnect")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False, index=True)
    tx_hash = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Numeric(20, 9), nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    transaction_type = Column(String)  # deposit, withdrawal
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    wallet = relationship("Wallet", back_populates="transactions")

# Обновим модель User для связи с кошельками
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Основные балансы
    ton_balance = Column(Float, default=0.0)
    stars_balance = Column(Float, default=0.0)
    
    # Крипто кошелек (оставляем для обратной совместимости)
    wallet_token = Column(String, nullable=True)
    
    # Язык и настройки
    language = Column(String, default="ru")
    
    # Реферальная система
    referrals_count = Column(Integer, default=0)
    active_referrals = Column(Integer, default=0)
    referral_earnings_usd = Column(Float, default=0.0)
    
    # Статистика по подаркам
    gifts_uploaded = Column(Integer, default=0)
    gift_name_number = Column(String, nullable=True)
    
    # Детальная статистика по рефералам
    stars_earned_from_refs = Column(Float, default=0.0)
    stars_spent_by_refs = Column(Float, default=0.0)
    total_refs_balance = Column(Float, default=0.0)
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    referrer = relationship(
        "User", 
        remote_side=[id],
        backref=backref("referrals", lazy="dynamic"),
        foreign_keys=[referrer_id]
    )
    
    deposits = relationship("DepositHistory", back_populates="user")
    crash_bets = relationship("CrashBetHistory", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")  # Добавляем связь с кошельками


class DepositHistory(Base):
    __tablename__ = "deposit_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    # Дата и время депозита
    deposit_datetime = Column(DateTime, default=func.now())
    amount = Column(Float, nullable=False)  # сумма депозита
    note = Column(String, nullable=True)  # примечание
    
    # Связь с пользователем
    user = relationship("User", back_populates="deposits")
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_deposit_user_date', 'user_id', 'deposit_datetime'),
        Index('idx_deposit_telegram_date', 'telegram_id', 'deposit_datetime'),
    )


class CrashBetHistory(Base):
    __tablename__ = "crash_bet_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    # Данные ставки
    bet_number = Column(Integer, nullable=False)  # номер ставки
    bet_amount = Column(Float, nullable=False)  # сумма ставки
    crash_coefficient = Column(Float, nullable=True)  # выигрышный коэф (null если проигрыш)
    win_amount = Column(Float, default=0.0)  # выигрышная сумма
    
    # Статус ставки
    status = Column(String, default='pending')  # pending, won, lost
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # Связь с пользователем
    user = relationship("User", back_populates="crash_bets")
    
    # Индексы для быстрой фильтрации
    __table_args__ = (
        Index('idx_crash_user_date', 'user_id', 'created_at'),
        Index('idx_crash_telegram_date', 'telegram_id', 'created_at'),
        Index('idx_crash_status', 'status'),
    )
    
    
class ReferralAction(Base):
    __tablename__ = "referral_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    referral_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    action_type = Column(String, nullable=False)  # 'registration', 'deposit', 'bet'
    action_amount = Column(Float, default=0.0)
    reward_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    
    # Связи
    referrer = relationship("User", foreign_keys=[referrer_id], backref="referral_actions_made")
    referral = relationship("User", foreign_keys=[referral_id], backref="referral_actions_received")
    
class CrashGameResult(Base):
    __tablename__ = "crash_game_results"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True, nullable=False)
    multiplier = Column(Numeric(10, 2), nullable=False)
    crashed_at = Column(Numeric(10, 2), nullable=False)
    total_players = Column(Integer, default=0)
    total_bet = Column(Numeric(20, 2), default=0.0)
    total_payout = Column(Numeric(20, 2), default=0.0)
    timestamp = Column(DateTime, default=func.now())
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_crash_game_id', 'game_id'),
        Index('idx_crash_timestamp', 'timestamp'),
    )