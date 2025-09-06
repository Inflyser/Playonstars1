# app/routers/stars.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.database.models import User
import time 

router = APIRouter()

@router.post("/stars/purchase")
async def purchase_stars(
    request: Request,
    purchase_data: dict,
    db: Session = Depends(get_db)
):
    """Покупка звезд"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        amount = float(purchase_data.get("amount", 0))
        
        # Проверяем минимальную сумму
        if amount < 100:
            raise HTTPException(status_code=400, detail="Minimum amount is 100 STARS")
        
        if amount > 5000:
            raise HTTPException(status_code=400, detail="Maximum amount is 5000 STARS")
        
        # Обновляем баланс
        user.stars_balance += amount
        db.commit()
        db.refresh(user)
        
        # Добавляем в историю транзакций
        transaction = crud.create_transaction(
            db=db,
            user_id=user.id,
            tx_hash=f"stars_purchase_{int(time.time())}",
            amount=amount,
            transaction_type="stars_purchase",
            status="completed"
        )
        
        return {
            "status": "success",
            "new_balance": user.stars_balance,
            "purchased_amount": amount,
            "transaction_id": transaction.id
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid amount format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stars/packages")
async def get_star_packages():
    """Получаем доступные пакеты звезд"""
    return {
        "packages": [
            {"id": 1, "amount": 100, "price": "1.99$", "bonus": 0},
            {"id": 2, "amount": 500, "price": "8.99$", "bonus": 50},
            {"id": 3, "amount": 1000, "price": "15.99$", "bonus": 150},
            {"id": 4, "amount": 5000, "price": "69.99$", "bonus": 1000}
        ]
    }