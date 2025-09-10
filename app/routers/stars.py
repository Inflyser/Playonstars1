from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging
from app.database.session import get_db
from app.dependencies import get_current_user
from app.database.models import User
from app.services.stars_service import stars_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create-invoice")
async def create_stars_invoice(
    request: Request,
    invoice_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание инвойса для оплаты Stars"""
    try:
        amount = int(invoice_data.get("amount", 0))
        
        if amount < 100:
            raise HTTPException(status_code=400, detail="Минимальная сумма 100 STARS")
        if amount > 5000:
            raise HTTPException(status_code=400, detail="Максимальная сумма 5000 STARS")
        
        # Здесь будет вызов Bot API для создания инвойса
        # Пока возвращаем данные для фронтенда
        return {
            "status": "success",
            "invoice_id": f"inv_{current_user.telegram_id}_{amount}",
            "amount": amount,
            "currency": "XTR",
            "description": f"Пополнение баланса на {amount} STARS"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат суммы")
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании инвойса")

@router.get("/payment-status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверка статуса платежа"""
    try:
        status_data = await stars_service.get_payment_status(payment_id)
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Платеж не найден")
        
        return {
            "status": status_data.get("status"),
            "amount": status_data.get("amount"),
            "currency": status_data.get("currency"),
            "user_id": status_data.get("user_id"),
            "timestamp": status_data.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при проверке статуса платежа")

@router.post("/webhook/stars")
async def handle_stars_webhook(request: Request, db: Session = Depends(get_db)):
    """Вебхук для уведомлений о платежах Stars"""
    try:
        payload = await request.json()
        logger.info(f"Stars webhook received: {payload}")
        
        # Обрабатываем разные типы вебхуков
        webhook_type = payload.get('type')
        
        if webhook_type == 'payment_succeeded':
            await handle_successful_payment(payload.get('data', {}), db)
        elif webhook_type == 'payment_failed':
            await handle_failed_payment(payload.get('data', {}), db)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

async def handle_successful_payment(payment_data: dict, db: Session):
    """Обработка успешного платежа"""
    # Эта логика уже реализована в successful_payment_handler
    pass

async def handle_failed_payment(payment_data: dict, db: Session):
    """Обработка неудачного платежа"""
    logger.warning(f"Payment failed: {payment_data}")
    pass