from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
import os
import json
import logging
from app.database.session import get_db
from app.database import crud
from app.services.stars_service import StarsService

router = APIRouter()
stars_service = StarsService()
logger = logging.getLogger(__name__)

@router.post("/create-invoice")
async def create_stars_invoice(
    request: Request,
    invoice_data: dict,
    db: Session = Depends(get_db)
):
    """Создание инвойса для оплаты Stars"""
    try:
        # ✅ Пытаемся получить telegram_id из сессии или из данных запроса
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            telegram_id = invoice_data.get("telegram_id")
        
        amount = invoice_data.get("amount")
        
        if not telegram_id or not amount:
            raise HTTPException(status_code=400, detail="Telegram ID and amount required")
        
        amount = int(amount)
        if amount < 10 or amount > 5000:  # ✅ Проверяем лимиты
            raise HTTPException(status_code=400, detail="Amount must be between 10 and 5000 STARS")
        
        # ✅ Проверяем существование пользователя
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Используем сервис для создания инвойса
        invoice_link = await stars_service.create_invoice(telegram_id, amount)
        
        if not invoice_link:
            raise HTTPException(status_code=500, detail="Failed to create invoice")
        
        return {
            "status": "success",
            "invoice_link": invoice_link
        }
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid amount format")
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