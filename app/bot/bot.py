from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
import os
from app.database.models import User
from app.database import crud  # ✅ Добавляем импорт crud

def webapp_builder():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Click",
        web_app=WebAppInfo(url=f"{os.getenv('FRONTEND_URL')}")
    )
    return builder.as_markup()

bot = Bot(
    os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

@asynccontextmanager
async def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DBSessionMiddleware:
    async def __call__(self, handler, event, data):
        async with get_db_session() as db:
            data["db"] = db
            return await handler(event, data)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.update.outer_middleware(DBSessionMiddleware())

async def process_referral(new_user_id: int, referrer_id: int, db: Session):
    """Обработка нового реферала
    Args:
        new_user_id (int): Внутренний ID нового пользователя в БД
        referrer_id (int): Внутренний ID пользователя-реферера в БД
    """
   
    print(f"🎯 Новый реферал: user {new_user_id} от referrer {referrer_id}")
    
    # Проверяем существует ли реферер по ID в БД
    referrer = db.query(User).filter(User.id == referrer_id).first()
    if not referrer:
        print(f"❌ Реферер {referrer_id} не найден в БД")
        # Дополнительная проверка: посмотрим всех пользователей в БД
        all_users = db.query(User.id, User.telegram_id).all()
        print(f"📊 Пользователи в БД: {all_users}")
        return False
    
    # Проверяем существует ли новый пользователь по ID в БД
    new_user = db.query(User).filter(User.id == new_user_id).first()
    if not new_user:
        print(f"❌ Новый пользователь {new_user_id} не найден в БД")
        return False
