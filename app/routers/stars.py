from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
import os
import json
import logging
from app.database.session import get_db
from app.dependencies import get_current_user
from app.database.models import User
from app.services.stars_service import stars_service  # Убери если не используется

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create-invoice")
async def create_stars_invoice(
    request: Request,  # Добавляем request для совместимости
    invoice_data: dict,  # Меняем на получение данных из body
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание инвойса для оплаты Stars через Bot API"""
    try:
        amount = invoice_data.get("amount")
        if not amount:
            raise HTTPException(status_code=400, detail="Не указана сумма")
        
        amount = int(amount)
        if amount < 10:
            raise HTTPException(status_code=400, detail="Минимальная сумма 100 STARS")
        
        # Создаем инвойс через Telegram Bot API
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise HTTPException(status_code=500, detail="BOT_TOKEN не настроен")
        
        url = f"https://api.telegram.org/bot{bot_token}/createInvoiceLink"
        
        payload = {
            "title": "Пополнение баланса STARS",
            "description": f"Пополнение игрового баланса на {amount} STARS",
            "payload": json.dumps({"user_id": current_user.telegram_id, "amount": amount}),
            "provider_token": "",  # ✅ ДЛЯ STARS ОСТАВЛЯЕМ ПУСТЫМ
            "currency": "XTR",     # ✅ ВАЛЮТА TELEGRAM STARS
            "prices": [{"label": f"{amount} STARS", "amount": amount}]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("ok"):
            return {
                "status": "success",
                "invoice_link": response_data["result"]
            }
        else:
            error_desc = response_data.get('description', 'Unknown error')
            logger.error(f"Telegram API error: {error_desc}")
            raise HTTPException(status_code=500, detail=f"Ошибка создания инвойса: {error_desc}")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат суммы")
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании инвойса")
    
    
    # app/routers/stars.py


# УБИРАЕМ ЛИШНИЕ ЭНДПОИНТЫ КОТОРЫЕ НЕ РАБОТАЮТ
# @router.get("/payment-status/{payment_id}") - УДАЛИ ЭТОТ ЕСЛИ stars_service НЕ РАБОТАЕТ
# @router.post("/webhook/stars") - УДАЛИ ЕСЛИ НЕ НАСТРОЕНЫ ВЕБХУКИ

# Оставляем только рабочий эндпоинт /create-invoice