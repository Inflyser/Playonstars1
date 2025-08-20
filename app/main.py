from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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

load_dotenv()

app = FastAPI()

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
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    
    # Получаем user_id из Telegram (пример для сообщений)
    user_id = update.message.from_user.id
    
    # Сохраняем в сессию
    request.session["user_id"] = user_id
    
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.post("/login")
async def login_from_webapp(request: Request, data: dict):
    tg_user = data.get("user")  # Данные из Telegram.WebApp
    request.session["user_id"] = tg_user["id"]
    return {"status": "ok"}