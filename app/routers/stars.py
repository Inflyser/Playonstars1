from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
import os
import json
import logging
from app.database.session import get_db
from app.database import crud

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create-invoice")
async def create_stars_invoice(
    request: Request,
    invoice_data: dict,
    db: Session = Depends(get_db)
):
    """Создание инвойса для оплаты Stars"""
    try:
        # Получаем telegram_id из сессии или запроса
        telegram_id = request.session.get("telegram_id") or invoice_data.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=400, detail="Telegram ID required")
        
        amount = invoice_data.get("amount")
        if not amount:
            raise HTTPException(status_code=400, detail="Amount required")
        
        amount = int(amount)
        if amount < 1:
            raise HTTPException(status_code=400, detail="Minimum amount is 1 STAR")
        
        # Проверяем пользователя
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")
        
        url = f"https://api.telegram.org/bot{bot_token}/createInvoiceLink"
        
        # ✅ ПРАВИЛЬНЫЙ формат для Stars
        payload = {
            "title": "PlayOnStars - Пополнение баланса",
            "description": f"Пополнение игрового баланса на {amount} STARS",
            "payload": json.dumps({
                "type": "stars_payment",
                "user_id": telegram_id,
                "amount": amount
            }),
            "provider_token": "",  # ✅ ДЛЯ STARS ОСТАВЛЯЕМ ПУСТЫМ
            "currency": "XTR",     # ✅ ВАЛЮТА TELEGRAM STARS
            "prices": [{
                "label": f"{amount} STARS",
                "amount": amount
            }]
        }
        
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("ok"):
            return {
                "status": "success",
                "invoice_link": response_data["result"]
            }
        else:
            error_desc = response_data.get('description', 'Unknown error')
            logger.error(f"Telegram API error: {error_desc}")
            raise HTTPException(status_code=500, detail=f"Invoice creation error: {error_desc}")
            
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def stars_webhook(request: Request, db: Session = Depends(get_db)):
    """Вебхук для обработки платежей Stars"""
    try:
        payload = await request.json()
        logger.info(f"Stars webhook received: {payload}")
        
        # Обрабатываем успешный платеж
        if payload.get('event') == 'payment_success':
            payment_data = payload.get('data', {})
            
            telegram_id = payment_data.get('user_id')
            amount = payment_data.get('amount')
            payment_id = payment_data.get('payment_id')
            
            if not all([telegram_id, amount, payment_id]):
                return {"status": "error", "message": "Missing data"}
            
            # Находим пользователя
            user = crud.get_user_by_telegram_id(db, telegram_id)
            if not user:
                return {"status": "error", "message": "User not found"}
            
            # Проверяем дубликат платежа
            if user.stars_payment_ids and payment_id in user.stars_payment_ids:
                return {"status": "success", "message": "Payment already processed"}
            
            # Зачисляем средства
            user.stars_balance += amount
            
            # Сохраняем ID платежа
            if user.stars_payment_ids is None:
                user.stars_payment_ids = []
            user.stars_payment_ids.append(payment_id)
            
            db.commit()
            
            logger.info(f"Added {amount} STARS to user {telegram_id}")
            
            return {"status": "success"}
        
        return {"status": "ignored", "message": "Event not handled"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}