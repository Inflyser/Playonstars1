from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Query
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
from app.database.models import User, CrashGameResult, ReferralAction
from urllib.parse import parse_qs
import secrets
import hmac
import hashlib
import json
import asyncio
from app.services.ton_service import ton_service
from app.database import crud
from app.database.session import SessionLocal
from app.services.crash_game import CrashGame
from app.routers import wallet
from app.routers import websocket
import random
from datetime import datetime 
from app.services.crash_game import CrashGame
from app.services.websocket_manager import websocket_manager
import websockets
from app.routers import stars

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
    "https://playonstars.netlify.app",  # Ваш фронтенд1
    "https://web.telegram.org",          # Telegram Web
    "https://telegram.org",              # Telegram
    "http://localhost:5173",
    "ws://localhost:5173",# Локальная разработка
    "https://tonconnect.io",  # ✅ Добавьте это
    "https://bridge.tonapi.io",  # ✅ И это
    os.getenv("FRONTEND_URL", "https://playonstars.netlify.app")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создайте экземпляр игры с передачей websocket_manager
crash_game = CrashGame(websocket_manager)
websocket_manager.set_crash_game(crash_game)  # ✅ Устанавливаем ссылку

# Запускаем health check
asyncio.create_task(websocket_manager.check_connection_health())



# ----------------------------- ЗАПУСК -------------------------------------



@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    
    # Telegram webhook
    webhook_url_telegram = os.getenv("WEBHOOK_URL_TELEGRAM")
    if webhook_url_telegram:
        await bot.set_webhook(webhook_url_telegram)
        print(f"📱 Telegram webhook set to: {webhook_url_telegram}")
    
    # TON webhook (пропускаем если не настроен)
    if os.getenv("TON_API_KEY") and os.getenv("TON_WALLET_ADDRESS"):
        print(f"🔗 Setting up TON webhook...")
        success = await ton_service.setup_webhook()
        if success:
            print("✅ TON Webhook successfully registered")
        else:
            print("⚠️ TON Webhook registration failed - continuing without")
    
    # Запускаем фоновую задачу для краш-игры
    asyncio.create_task(run_crash_game())
    try:
        import websockets
        print("✅ WebSocket support: websockets library installed")
    except ImportError:
        print("❌ WebSocket support: websockets library missing")
        
    try:
        import wsproto
        print("✅ WebSocket support: wsproto library installed") 
    except ImportError:
        print("❌ WebSocket support: wsproto library missing")


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


@app.get("/api/debug/session")
async def debug_session(request: Request):
    return {
        "session": dict(request.session),
        "headers": dict(request.headers)
    }
    
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



@app.post("/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        # ✅ Очищаем сессию перед обработкой Telegram webhook
        request.session.clear()
        
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
        
        # ✅ Сохраняем только примитивные данные
        if user_id:
            request.session["user_id"] = user_id
            
            # ❌ УДАЛЯЕМ эту строку (она вызывает ошибку):
            # request.session["telegram_data"] = update.model_dump()
            
            # ✅ Вместо этого сохраняем только минимальные нужные данные:
            telegram_data = {}
            if update.message:
                telegram_data = {
                    "update_id": update.update_id,
                    "message_id": update.message.message_id,
                    "text": update.message.text,
                    "from_id": update.message.from_user.id if update.message.from_user else None,
                    "chat_id": update.message.chat.id if update.message.chat else None
                }
            elif update.callback_query:
                telegram_data = {
                    "update_id": update.update_id,
                    "callback_query_id": update.callback_query.id,
                    "data": update.callback_query.data,
                    "from_id": update.callback_query.from_user.id if update.callback_query.from_user else None
                }
            
            request.session["telegram_data"] = telegram_data
        
        await dp.feed_update(bot, update)
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error in telegram webhook: {e}")
        return {"status": "error", "message": str(e)}
    
    
    

# ----------------------------- Веб-сокет -------------------------------------



@app.get("/api/websocket/status")
async def websocket_status():
    """Проверка статуса WebSocket"""
    try:
        import websockets
        import wsproto
        return {
            "websockets_installed": True,
            "wsproto_installed": True,
            "crash_connections": len(websocket_manager.crash_game_connections),
            "total_connections": sum(len(conns) for conns in websocket_manager.active_connections.values())
        }
    except ImportError:
        return {
            "websockets_installed": False,
            "wsproto_installed": False,
            "error": "WebSocket libraries not installed"
        }

async def run_crash_game():
    """Фоновая задача для управления краш-игрой"""
    while True:
        try:
            await crash_game.run_game_cycle()  # ✅ Используем существующий экземпляр
            # Пауза между играми
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Error in crash game: {e}")
            await asyncio.sleep(10)
        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket, "general")
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка сообщений
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": message.get("timestamp")})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "general")

@app.websocket("/ws/crash")
async def websocket_crash(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect_crash_game(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📨 [WebSocket] Received message: {data}")
            
            try:
                message = json.loads(data)
                print(f"📨 [WebSocket] Parsed message: {message}")
                
                if message.get("type") == "place_bet":
                    print("🎯 [WebSocket] Processing place_bet message")
                    await websocket_manager.handle_crash_bet(websocket, message)
                elif message.get("type") == "ping":
                    # Обрабатываем ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                    
            except json.JSONDecodeError as e:
                print(f"❌ [WebSocket] JSON decode error: {e}")
                
    except WebSocketDisconnect:
        print("🔌 [WebSocket] Client disconnected from crash game")
        websocket_manager.disconnect_crash_game(websocket)
        
        
@app.websocket("/ws/user/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: int):
    await websocket_manager.connect(websocket, f"user_{user_id}")
    try:
        while True:
            data = await websocket.receive_text()
            # Персональные сообщения для пользователя
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, f"user_{user_id}")
    
    
async def check_deposits_periodically():
    """Периодическая проверка депозитов (fallback)"""
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
            await asyncio.sleep(300)  # Проверяем каждые 5 минут (вместо 1)
            
        except Exception as e:
            print(f"Error in deposit check: {e}")
            await asyncio.sleep(300)
            


@app.websocket("/ws/crash")
async def websocket_crash_endpoint(websocket: WebSocket):
    await websocket_manager.connect_crash_game(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка ставок краш-игры
            try:
                message = json.loads(data)
                if message.get("type") == "place_bet":
                    # Здесь логика обработки ставки
                    user_id = message.get("user_id")
                    amount = message.get("amount")
                    auto_cashout = message.get("auto_cashout")
                    
                    # Сохраняем ставку
                    if user_id and amount:
                        crash_game.bets[user_id] = {
                            "amount": amount,
                            "auto_cashout": auto_cashout,
                            "placed_at": datetime.now()
                        }
                        
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        websocket_manager.disconnect_crash_game(websocket)

        


@app.get("/api/ws/test")
async def websocket_test():
    return {
        "websocket_enabled": True,
        "crash_connections": len(websocket_manager.crash_game_connections),
        "allowed_origins": [
            "https://playonstars.netlify.app",
            "https://web.telegram.org"
        ]
    }
    
        
        
# ----------------------------- Кошелек -------------------------------------
      
      
        
# Добавьте этот эндпоинт для проверки депозитов
@app.get("/api/wallet/check-deposits")
async def check_user_deposits(
    request: Request,
    db: Session = Depends(get_db)
):
    """Проверяем депозиты пользователя"""
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем все pending транзакции пользователя
    pending_txs = crud.get_pending_transactions(db, user.id)
    
    return {
        "pending_transactions": [
            {
                "tx_hash": tx.tx_hash,
                "amount": float(tx.amount),
                "created_at": tx.created_at.isoformat()
            }
            for tx in pending_txs
        ]
    }
        
@app.post("/api/wallet/deposit")
async def create_deposit(
    request: Request,
    deposit_data: dict,
    db: Session = Depends(get_db)
):
    """Создаем запись о депозите"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Создаем pending транзакцию
        transaction = crud.create_transaction(
            db=db,
            user_id=user.id,
            tx_hash=deposit_data.get("tx_hash"),
            amount=float(deposit_data.get("amount", 0)),
            transaction_type="deposit",
            status="pending"
        )
        
        return {
            "status": "success",
            "transaction_id": transaction.id,
            "message": "Transaction created, waiting for confirmation"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/api/wallet/transaction/{tx_hash}")
async def get_transaction_status(
    tx_hash: str,
    db: Session = Depends(get_db)
):
    """Проверяем статус транзакции"""
    transaction = crud.get_transaction_by_hash(db, tx_hash)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "tx_hash": transaction.tx_hash,
        "status": transaction.status,
        "amount": float(transaction.amount),
        "created_at": transaction.created_at.isoformat()
    }



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




# ----------------------------- USER API -------------------------------------



@app.post("/api/user/sync-balance")
async def sync_user_balance(
    request: Request,
    balance_data: dict,
    db: Session = Depends(get_db)
):
    """Синхронизация баланса с клиентом"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Просто возвращаем актуальный баланс из БД
        return {
            "stars_balance": user.stars_balance,
            "ton_balance": user.ton_balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/api/user/update-balance")
async def update_user_balance(
    request: Request,
    balance_data: dict,
    db: Session = Depends(get_db)
):
    """Обновляем баланс пользователя"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        currency = balance_data.get("currency")
        amount = float(balance_data.get("amount", 0))
        operation = balance_data.get("operation", "add")  # add или set
        
        if currency == "stars":
            if operation == "add":
                user.stars_balance += amount
            else:  # set
                user.stars_balance = amount
        elif currency == "ton":
            if operation == "add":
                user.ton_balance += amount
            else:  # set
                user.ton_balance = amount
        
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "balance": {
                "stars_balance": user.stars_balance,
                "ton_balance": user.ton_balance
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
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

    
@app.post("/api/user/wallet")
async def save_user_wallet(
    request: Request,
    wallet_data: dict,
    db: Session = Depends(get_db)
):
    """Сохраняем адрес кошелька пользователя"""
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = crud.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем или создаем запись кошелька
    wallet = crud.get_wallet_by_user(db, user.id)
    if wallet:
        wallet.address = wallet_data.get("wallet_address")
        wallet.wallet_provider = wallet_data.get("wallet_provider", "tonconnect")
    else:
        wallet = crud.create_wallet(
            db, 
            user.id, 
            wallet_data.get("wallet_address"), 
            wallet_data.get("wallet_provider", "tonconnect")
        )
    
    db.commit()
    
    return {"status": "success", "wallet_id": wallet.id}

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
        "referral_link": f"https://t.me/Playonstars_bot?start=ref_{user.id}"
    }
    

@app.get("/api/user/referral-transactions")
async def get_referral_transactions(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получаем историю реферальных транзакций"""
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Получаем транзакции реферальной системы
        transactions = db.query(ReferralAction).filter(
            ReferralAction.referrer_id == user_id
        ).order_by(
            ReferralAction.created_at.desc()
        ).limit(limit).all()
        
        return {
            "transactions": [
                {
                    "id": transaction.id,
                    "action_type": transaction.action_type,
                    "action_amount": float(transaction.action_amount),
                    "reward_amount": float(transaction.reward_amount),
                    "created_at": transaction.created_at.isoformat(),
                    "referral_id": transaction.referral_id
                }
                for transaction in transactions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/user/referral-withdraw")
async def withdraw_referral_earnings(
    request: Request,
    db: Session = Depends(get_db)
):
    """Вывод реферальных earnings"""
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.stars_earned_from_refs <= 0:
            raise HTTPException(status_code=400, detail="No earnings to withdraw")
        
        # Добавляем earnings к основному балансу
        user.stars_balance += user.stars_earned_from_refs
        
        # Создаем запись о выводе
        withdrawal = ReferralAction(
            referrer_id=user_id,
            referral_id=user_id,  # self-reference для вывода
            action_type='withdrawal',
            action_amount=user.stars_earned_from_refs,
            reward_amount=user.stars_earned_from_refs
        )
        
        # Обнуляем earned amount
        user.stars_earned_from_refs = 0
        
        db.add(withdrawal)
        db.commit()
        
        return {
            "status": "success",
            "withdrawn_amount": user.stars_earned_from_refs,
            "new_balance": user.stars_balance
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

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



    
    
# ----------------------------- КРАШ ИГРА -------------------------------------



    
@app.get("/games/crash/history")
async def get_crash_history(limit: int = 50, db: Session = Depends(get_db)):
    """Получить историю краш-игр из базы данных"""
    try:
        results = crud.get_crash_game_history(db, limit)
        return {
            "history": [
                {
                    "game_id": result.game_id,
                    "multiplier": float(result.multiplier),
                    "crashed_at": float(result.crashed_at),
                    "total_players": result.total_players,
                    "total_bet": float(result.total_bet),
                    "total_payout": float(result.total_payout),
                    "timestamp": result.timestamp.isoformat()
                }
                for result in results
            ]
        }
    except Exception as e:
        print(f"Error getting crash history: {e}")
        return {"history": []}
    


@app.post("/api/games/crash/bet")
async def make_crash_bet(request: Request, bet_data: dict, db: Session = Depends(get_db)):
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
        
        # ✅ ИСПРАВЛЯЕМ ВЫЗОВ ФУНКЦИИ:
        user = update_user_balance(db, telegram_id, currency, -amount)
        
        # Создаем запись о ставке
        bet = add_crash_bet(db, user_id, telegram_id, amount)
        
        return {
            "status": "success",
            "bet_id": bet.id,
            "bet_number": bet.bet_number,
            "new_balance": user.stars_balance if currency == "stars" else user.ton_balance
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Пример FastAPI endpoint
@app.get("/crash/history")
async def get_crash_history(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)  # ← ДОБАВЬТЕ ЭТУ СТРОЧКУ
):
    history = db.query(CrashGameResult)\
        .order_by(CrashGameResult.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return [
        {
            "gameId": game.game_id,
            "multiplier": float(game.multiplier),
            "crashedAt": float(game.crashed_at),
            "timestamp": game.timestamp.isoformat(),
            "playersCount": game.total_players,
            "totalBet": float(game.total_bet),
            "totalPayout": float(game.total_payout)
        }
        for game in history
    ]


@app.get("/api/crash/bet-history")
async def get_crash_bet_history(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Получаем историю ставок краш-игры"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем всю историю ставок
        bets = crud.get_all_crash_bet_history(db, limit)
        
        return {
            "bets": [
                {
                    "id": bet.id,
                    "bet_number": bet.bet_number,
                    "user_id": bet.user_id,
                    "telegram_id": bet.telegram_id,
                    "bet_amount": float(bet.bet_amount),
                    "crash_coefficient": float(bet.crash_coefficient) if bet.crash_coefficient else None,
                    "win_amount": float(bet.win_amount),
                    "status": bet.status,
                    "created_at": bet.created_at.isoformat(),
                    "ended_at": bet.ended_at.isoformat() if bet.ended_at else None
                }
                for bet in bets
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------- ОСТАЛЬНЫЕ -------------------------------------



    
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
app.include_router(wallet.router, prefix="/api")
app.include_router(stars.router, prefix="/api")
app.include_router(websocket.router)