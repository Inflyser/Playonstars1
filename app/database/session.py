from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ ВАЖНО: Для Render PostgreSQL нужно добавить sslmode=require
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

# Создаем engine с правильными настройками SSL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Для отладки
    pool_pre_ping=True,  # ✅ Проверяем соединение перед использованием
    pool_recycle=300,  # ✅ Пересоздаем соединения каждые 5 минут
    connect_args={
        'sslmode': 'require',
        'sslrootcert': '/etc/ssl/certs/ca-certificates.crt'
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()