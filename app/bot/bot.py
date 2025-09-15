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
from app.database.models import User, ReferralAction
from app.database import crud  # ✅ Добавляем импорт crud
from aiogram.types import LabeledPrice, PreCheckoutQuery

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
            try:
                # ✅ ВАЖНО: Всегда вызываем handler
                result = await handler(event, data)
                return result
            except Exception as e:
                print(f"Middleware error: {e}")
                # ❌ НЕ ПРОПУСКАЙТЕ ВЫЗОВ handler!
                raise

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.update.outer_middleware(DBSessionMiddleware())

async def process_referral(new_user_id: int, referrer_id: int, db: Session):
    """Обработка нового реферала"""
    try:
        print(f"🎯 Новый реферал: user {new_user_id} от referrer {referrer_id}")
        
        # Проверяем существует ли реферер по ID в БД
        referrer = db.query(User).filter(User.id == referrer_id).first()
        if not referrer:
            print(f"❌ Реферер {referrer_id} не найден в БД")
            # Дополнительная диагностика
            all_users = db.query(User.id, User.telegram_id).all()
            print(f"📊 Все пользователи в БД: {[(u.id, u.telegram_id) for u in all_users]}")
            return False
        
        # Проверяем существует ли новый пользователь по ID в БД
        new_user = db.query(User).filter(User.id == new_user_id).first()
        if not new_user:
            print(f"❌ Новый пользователь {new_user_id} не найден в БД")
            return False
        
        print(f"✅ Реферер найден: {referrer.id} (telegram_id: {referrer.telegram_id})")
        print(f"✅ Новый пользователь найден: {new_user.id} (telegram_id: {new_user.telegram_id})")
        
        # Обновляем реферальную статистику
        referrer.referrals_count += 1
        referrer.active_referrals += 1
        
        # Устанавливаем реферера для нового пользователя
        new_user.referrer_id = referrer_id
        
        # Создаем запись в referral_actions
        referral_action = ReferralAction(
            referrer_id=referrer_id,
            referral_id=new_user_id,
            action_type='registration',
            action_amount=0.0,
            reward_amount=0.0
        )
        db.add(referral_action)
        
        db.commit()
        print(f"✅ Реферал успешно обработан: {new_user_id} -> {referrer_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обработки реферала: {e}")
        import traceback
        traceback.print_exc()  # Выводим полную трассировку ошибки
        db.rollback()
        return False
    
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    # ✅ Всегда отвечаем OK на pre_checkout_query
    await pre_checkout_query.answer(ok=True)
    
    
