from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Настройки SSL только в connect_args, НЕ меняем URL!
connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    connect_args = {
        'sslmode': 'require',
        'sslrootcert': '/etc/ssl/certs/ca-certificates.crt'
    }

# Создаем engine с правильными настройками SSL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Для отладки
    pool_pre_ping=True,  # ✅ Проверяем соединение перед использованием
    pool_recycle=300,  # ✅ Пересоздаем соединения каждые 5 минут
    connect_args=connect_args  # ✅ Только здесь настройки SSL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()