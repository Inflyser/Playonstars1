from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    gold_eggs = Column(Integer, default=0)
    normal_eggs = Column(Integer, default=0)
    last_active = Column(DateTime)
    duck_state = Column(String, default="idle")

    # Новые поля
    total_donations = Column(Float, default=0.0)  # сумма донатов
    referrals_count = Column(Integer, default=0)  # кол-во рефералов
    rank = Column(String, default="beginner")     # ранг
    skill_level = Column(Integer, default=1)      # скилл/уровень
    completed_tasks = Column(Integer, default=0)  # выполнено заданий
    total_logins = Column(Integer, default=0)     # сколько раз заходил за все время
    daily_logins = Column(Integer, default=0)      # сколько раз заходил сегодня
    farming_start = Column(DateTime, nullable=True)  # время начала фарма
    farming_end = Column(DateTime, nullable=True)    # время окончания фарма
    language = Column(String, default="ru")       # язык (ru/en)