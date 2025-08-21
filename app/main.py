from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from app.database.session import engine, Base
from app.bot.bot import bot, dp
from aiogram.types import Update
from app.routers.telegram import router as telegram_router
import os
from app.database.crud import get_user_language
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.models import User
import secrets

load_dotenv()

app = FastAPI()

# Добавьте SessionMiddleware ПЕРВЫМ
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", secrets.token_hex(32)),
    session_cookie="session",
    max_age=3600 * 24 * 7,  # 7 дней
    same_site="none",
    https_only=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup(): 
    Base.metadata.create_all(bind=engine)
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")
        
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
        
        # Сохраняем в сессию
        if user_id:
            request.session["user_id"] = user_id
            request.session["telegram_data"] = update.to_python()
        
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
        
        language = get_user_language(db, user_id)
        return {"language": language}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/user/data")
async def get_user_data(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return {"error": "Not authenticated"}
        
        user_data = request.session.get("telegram_user", {})
        return {"user_data": user_data}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "DuckTMA Bot is running"}

# Подключаем роутеры
app.include_router(telegram_router)