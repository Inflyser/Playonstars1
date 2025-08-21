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



def webapp_builder():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Click",
        web_app=WebAppInfo(url=f"{os.getenv('FRONTEND_URL')}/index.html")
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


# Правильная реализация middleware для aiogram
class DBSessionMiddleware:
    async def __call__(self, handler, event, data):
        async with get_db_session() as db:
            data["db"] = db
            return await handler(event, data)

# Создаем хранилище для FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Правильное добавление middleware
dp.update.outer_middleware(DBSessionMiddleware())  # ← ИСПРАВЛЕНО