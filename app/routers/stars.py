from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import crud
from app.database.session import get_db
from app.dependencies import get_current_user
from app.database.models import User
import os

router = APIRouter()

@router.post("/purchase")
async def purchase_stars(
    request: Request,
    purchase_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Покупка Stars через Telegram WebApp
    """
    try:
        amount = float(purchase_data.get("amount", 0))
        
        if amount < 100:
            raise HTTPException(status_code=400, detail="Минимальная сумма 100 STARS")
        
        # Здесь будет логика создания инвойса в Telegram
        # Пока просто добавляем Stars к балансу
        user = crud.update_user_balance(db, current_user.telegram_id, "stars", amount)
        
        return {
            "status": "success",
            "amount": amount,
            "new_balance": user.stars_balance
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверная сумма")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-invoice")
async def create_stars_invoice(
    request: Request,
    invoice_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание инвойса для оплаты Stars
    """
    try:
        amount = int(invoice_data.get("amount", 0))
        description = invoice_data.get("description", "Пополнение STARS")
        
        # Здесь будет вызов Telegram Bot API для создания инвойса
        # Пока заглушка
        return {
            "status": "success",
            "invoice_id": f"inv_{current_user.id}_{amount}",
            "amount": amount,
            "description": description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))