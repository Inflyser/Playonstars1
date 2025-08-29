from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from app.database.session import engine, Base
from app.bot.bot import bot, dp
from aiogram.types import Update
from app.routers.telegram import router as telegram_router
from app.routers import wallet
import os
from app.database.crud import get_user_by_telegram_id
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.models import User
from urllib.parse import parse_qs
import secrets
import hmac
import hashlib
import json
import asyncio
from app.services.ton_service import ton_service
from app.database import crud
from app.database.session import SessionLocal

from app.database.crud import (
    get_user_by_telegram_id, 
    create_user, 
    update_user_balance,
    get_user_balance,
    add_deposit_history,
    add_crash_bet
)


load_dotenv()

app = FastAPI()

# Добавьте SessionMiddleware ПЕРВЫМ
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", secrets.token_hex(32)),
    session_cookie="session",
    max_age=3600 * 24 * 7,  # 7 дней
    same_site="none",
    https_only=True if os.getenv("ENVIRONMENT") == "development" else False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://playonstars.netlify.app",  # Ваш фронтенд
    "https://web.telegram.org",          # Telegram Web
    "https://telegram.org",              # Telegram
    "http://localhost:5173",             # Локальная разработка
    os.getenv("FRONTEND_URL", "https://playonstars.netlify.app")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def check_deposits_periodically():
    """Периодическая проверка депозитов"""
    while True:
        try:
            db = SessionLocal()
            deposits = await ton_service.check_deposits_to_wallet()
            
            for deposit in deposits:
                # Проверяем не обрабатывали ли уже эту транзакцию
                existing_tx = crud.get_transaction_by_hash(db, deposit['tx_hash'])
                if not existing_tx:
                    print(f"New deposit detected: {deposit}")
                    # Здесь логика обработки депозита
                    
            db.close()
            await asyncio.sleep(60)  # Проверяем каждую минуту
            
        except Exception as e:
            print(f"Error in deposit check: {e}")
            await asyncio.sleep(60)

from app.services.ton_service import ton_service

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    webhook_url = os.getenv("WEBHOOK_URL_TELEGRAM")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        print(f"Telegram webhook set to: {webhook_url}")
    
    # Настраиваем TON webhook
    await ton_service.setup_webhook()

@app.post("/api/webhook/ton")
async def ton_webhook(request: Request):
    """Эндпоинт для получения веб-перехватчиков от TON API"""
    try:
        payload = await request.json()
        return await ton_service.process_webhook(request, payload)
    except Exception as e:
        print(f"TON webhook error: {e}")
        return {"status": "error", "message": str(e)}
    
@app.get("/api/ton/status")
async def ton_status():
    """Проверка статуса TON интеграции"""
    return {
        "ton_api_connected": bool(os.getenv("TON_API_KEY")),
        "wallet_address": os.getenv("TON_WALLET_ADDRESS"),
        "webhook_url": f"{os.getenv('WEBHOOK_URL_TON')}/api/webhook/ton",
        "has_wallet_secret": bool(os.getenv("TON_WALLET_SECRET"))
    }

        
@app.post("/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        update = Update(**data)
        
        # Получаем user_id из Telegram update
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        elif update.inline_query:
            user_id = update.inline_query.from_user.id
        else:
            user_id = None
        
        # Сохраняем в сессию (ИСПРАВЛЕННАЯ СТРОКА)
        if user_id:
            request.session["user_id"] = user_id
            # Используем model_dump() вместо to_python()
            request.session["telegram_data"] = update.model_dump()
        
        await dp.feed_update(bot, update)
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error in telegram webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/login")
async def login_from_webapp(request: Request, data: dict, db: Session = Depends(get_db)):
    try:
        tg_user = data.get("user", {})
        user_id = tg_user.get("id")
        
        if user_id:
            # Сохраняем данные пользователя в сессию
            request.session["user_id"] = user_id
            request.session["telegram_user"] = tg_user
            
            # Проверяем/создаем пользователя в БД
            from app.database.crud import get_user, create_user
            user = get_user(db, user_id)
            if not user:
                user = create_user(db, user_id, tg_user.get("username"))
            
            return {"status": "ok", "user_id": user_id}
        else:
            return {"status": "error", "message": "No user data"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/user/language")
async def get_user_language_api(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return {"error": "Not authenticated"}
        
        # Получаем пользователя и его язык
        user = get_user_by_telegram_id(db, user_id)
        language = user.language if user else 'ru'
        
        return {"language": language}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/user/data")
async def get_user_data(request: Request, db: Session = Depends(get_db)):
    try:
        telegram_id = request.session.get("telegram_id")  # ← Используем telegram_id
        if not telegram_id:
            return {"error": "Not authenticated"}
        
        # Получаем данные из БД, а не из сессии
        user = get_user_by_telegram_id(db, telegram_id)
        if not user:
            return {"error": "User not found"}
        
        return {
            "user_data": {
                "id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Bot is running"}


def verify_telegram_webapp(init_data: str) -> bool:
    """Проверяем подпись Telegram Web App"""
    try:
        # Парсим query string
        parsed_data = parse_qs(init_data)
        
        # Извлекаем хэш
        received_hash = parsed_data.get('hash', [''])[0]
        if not received_hash:
            return False
        
        # Создаем data_check_string
        data_check_parts = []
        for key in sorted(parsed_data.keys()):
            if key != 'hash':
                values = parsed_data[key]
                if values:
                    data_check_parts.append(f"{key}={values[0]}")
        
        data_check_string = "\n".join(data_check_parts)
        
        # Секретный ключ
        bot_token = os.getenv("BOT_TOKEN", "")
        if not bot_token:
            return False
        
        # Создаем secret key
        secret_key = hmac.new(
            b"WebAppData", 
            bot_token.encode(), 
            hashlib.sha256
        ).digest()
        
        # Вычисляем хэш
        computed_hash = hmac.new(
            secret_key, 
            data_check_string.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return computed_hash == received_hash
        
    except Exception as e:
        print(f"Verify error: {e}")
        return False

def parse_telegram_data(init_data: str) -> dict:
    """Парсим данные пользователя из initData"""
    try:
        parsed_data = parse_qs(init_data)
        
        user_str = parsed_data.get('user', [''])[0]
        if user_str:
            user_data = json.loads(user_str)
            
            # ✅ ВАЖНО: Проверяем все поля которые приходят
            print(f"🎯 User data keys: {list(user_data.keys())}")
            print(f"📸 Photo URL exists: {'photo_url' in user_data}")
            print(f"📸 Photo URL value: {user_data.get('photo_url')}")
            print(f"👤 First name: {user_data.get('first_name')}")
            print(f"👤 Username: {user_data.get('username')}")
            print(f"🆔 ID: {user_data.get('id')}")
            
            return user_data

        return {}
        
    except Exception as e:
        print(f"Parse error: {e}")
        return {}

# Альтернативная упрощенная версия проверки (если первая не работает)
def verify_telegram_webapp_simple(init_data: str) -> bool:
    """Упрощенная проверка для разработки"""
    current_env = os.getenv("ENVIRONMENT", "development")
    print(f"🛠️ Current environment: {current_env}")
    
    if current_env == "production":
        # Полная проверка в production
        print("🔒 Production mode - full verification")
        try:
            parsed_data = parse_qs(init_data)
            return 'user' in parsed_data and 'hash' in parsed_data
        except:
            return False
    else:
        # В development пропускаем проверку
        print("⚠️ Development mode - skipping Telegram verification")
        return True

@app.post("/api/auth/telegram")
async def auth_telegram(request: Request, db: Session = Depends(get_db)):
    try:
        print("🔐 Auth endpoint called")
        data = await request.json()
        
        init_data = data.get("initData")
        if not init_data:
            raise HTTPException(status_code=400, detail="No initData provided")
        
        if not verify_telegram_webapp_simple(init_data):
            raise HTTPException(status_code=401, detail="Invalid Telegram data")
        
        user_data = parse_telegram_data(init_data)
        telegram_id = user_data.get("id")
        
        if not telegram_id:
            raise HTTPException(status_code=400, detail="No user data in initData")
        
        # ✅ Логируем что приходит от Telegram
        print(f"📸 Telegram photo_url: {user_data.get('photo_url')}")
        print(f"👤 Telegram first_name: {user_data.get('first_name')}")
        print(f"👤 Telegram last_name: {user_data.get('last_name')}")
        
        # Проверяем/создаем пользователя в БД
        user = get_user_by_telegram_id(db, telegram_id)
        if not user:
            # ✅ СОЗДАЕМ с photo_url
            user = create_user(
                db=db,
                telegram_id=telegram_id,
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                photo_url=user_data.get("photo_url")  # ✅ ВАЖНО!
            )
            print(f"Created new user: {user.id}")
        else:
            print(f"Found existing user: {user.id}")
            
            # ✅ ОБНОВЛЯЕМ отсутствующие данные
            update_fields = False
            
            if not user.first_name and user_data.get("first_name"):
                user.first_name = user_data.get("first_name")
                update_fields = True
                
            if not user.last_name and user_data.get("last_name"):
                user.last_name = user_data.get("last_name")
                update_fields = True
                
            if not user.photo_url and user_data.get("photo_url"):
                user.photo_url = user_data.get("photo_url")
                update_fields = True
            
            if update_fields:
                db.commit()
                db.refresh(user)
                print(f"✅ Updated user data in DB")
        
        # ✅ Логируем что сохранилось в БД
        print(f"💾 DB photo_url: {user.photo_url}")
        print(f"💾 DB first_name: {user.first_name}")
        print(f"💾 DB last_name: {user.last_name}")
        
        # Сохраняем в сессию
        request.session["user_id"] = user.id
        request.session["telegram_id"] = user.telegram_id
        request.session["telegram_user"] = {
            "id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url  # ✅ Добавляем в сессию
        }
        
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "ton_balance": user.ton_balance,
                "stars_balance": user.stars_balance,
                "photo_url": user.photo_url  # ✅ Берем из БД
            }
        }
        
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/balance")
async def get_balance(request: Request, db: Session = Depends(get_db)):
    """Получаем баланс пользователя"""
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "ton_balance": user.ton_balance,
        "stars_balance": user.stars_balance
    }

@app.post("/api/user/deposit")
async def make_deposit(
    request: Request,
    deposit_data: dict,
    db: Session = Depends(get_db)
):
    """Создаем депозит"""
    telegram_id = request.session.get("telegram_id")
    user_id = request.session.get("user_id")
    
    if not telegram_id or not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        amount = float(deposit_data.get("amount", 0))
        currency = deposit_data.get("currency", "ton")
        note = deposit_data.get("note", "")
        
        # Обновляем баланс
        user = update_user_balance(db, telegram_id, currency, amount)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Добавляем в историю
        deposit = add_deposit_history(db, user_id, telegram_id, amount, note)
        
        return {
            "status": "success",
            "new_balance": user.ton_balance if currency == "ton" else user.stars_balance,
            "deposit_id": deposit.id
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid amount")

@app.post("/api/games/crash/bet")
async def make_crash_bet(
    request: Request,
    bet_data: dict,
    db: Session = Depends(get_db)
):
    """Делаем ставку в crash игру"""
    telegram_id = request.session.get("telegram_id")
    user_id = request.session.get("user_id")
    
    if not telegram_id or not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        amount = float(bet_data.get("amount", 0))
        currency = bet_data.get("currency", "stars")
        
        # Проверяем достаточно ли средств
        user = get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if currency == "stars" and user.stars_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient stars balance")
        elif currency == "ton" and user.ton_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient ton balance")
        
        # Списываем средства
        user = update_user_balance(db, telegram_id, currency, -amount)
        
        # Создаем запись о ставке
        bet = add_crash_bet(db, user_id, telegram_id, amount)
        
        return {
            "status": "success",
            "bet_id": bet.id,
            "bet_number": bet.bet_number,
            "new_balance": user.stars_balance if currency == "stars" else user.ton_balance
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    
@app.get("/api/user/referral-info")
async def get_referral_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получаем реферальную информацию"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "referrals_count": user.referrals_count,
        "active_referrals": user.active_referrals,
        "referral_earnings_usd": user.referral_earnings_usd,
        "stars_earned_from_refs": user.stars_earned_from_refs,
        "stars_spent_by_refs": user.stars_spent_by_refs,
        "total_refs_balance": user.total_refs_balance,
        "referral_link": f"https://t.me/your_bot?start=ref_{user.id}"
    }
    
@app.get("/api/debug/session")
async def debug_session(request: Request):
    return {
        "session": dict(request.session),
        "headers": dict(request.headers)
    }
    
@app.get("/api/webhook-info")
async def webhook_info():
    webhook_url = os.getenv("WEBHOOK_URL")
    bot_info = await bot.get_me()
    
    return {
        "bot_username": bot_info.username,
        "webhook_url": webhook_url,
        "webhook_set": await bot.get_webhook_info() if webhook_url else False
    }


@app.get("/api/top/users")
async def get_top_users(
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """Получаем топ пользователей по stars_balance"""
    try:
        top_users = db.query(User)\
            .order_by(User.stars_balance.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return {
            "users": [
                {
                    "rank": offset + i + 1,
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "stars_balance": user.stars_balance,
                    # ✅ Умная генерация аватарки
                    "photo_url": generate_avatar_url(user)
                }
                for i, user in enumerate(top_users)
            ],
            "total": db.query(User).count()
        }
        
    except Exception as e:
        print(f"Error getting top users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def generate_avatar_url(user: User) -> str:
    """Генерирует URL аватарки с fallback логикой"""
    # Если у пользователя есть фото в БД
    if user.photo_url:
        return user.photo_url
    
    # Если есть username - пробуем через него
    if user.username:
        return f"https://t.me/i/userpic/320/{user.username}.jpg"
    
    # Если нет username - используем дефолтную аватарку
    return f"https://t.me/i/userpic/320/{user.telegram_id}.jpg"
    
    
# Подключаем роутеры
dp.include_router(telegram_router)
app.include_router(wallet.router)