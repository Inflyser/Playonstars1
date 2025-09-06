from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.services.ton_service import ton_service

router = APIRouter()

@router.get("/wallet/balance/{address}")
async def get_wallet_balance(address: str, db: Session = Depends(get_db)):
    """Получаем баланс кошелька"""
    try:
        balance = await ton_service.get_wallet_balance(address)
        return {"balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wallet/transaction")
async def create_transaction(transaction_data: dict, db: Session = Depends(get_db)):
    """Создаем запись о транзакции"""
    try:
        transaction = crud.create_transaction(
            db=db,
            tx_hash=transaction_data.get("tx_hash"),
            amount=float(transaction_data.get("amount", 0)),
            transaction_type=transaction_data.get("type", "deposit"),
            status="pending"
        )
        return {"status": "success", "transaction_id": transaction.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wallet/transaction/{tx_hash}")
async def get_transaction_status(tx_hash: str, db: Session = Depends(get_db)):
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
    
@router.get("/wallet/check-deposits")  # ← Добавить этот эндпоинт
async def check_user_deposits(
    request: Request,  # ← Добавить параметр Request
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