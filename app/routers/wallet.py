from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import crud, models
from app.database.session import get_db
from app.services.ton_service import ton_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("/connect")
async def connect_wallet(
    wallet_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Подключаем кошелек к аккаунту"""
    try:
        address = wallet_data.get("address")
        if not address:
            raise HTTPException(status_code=400, detail="Wallet address required")
        
        # Проверяем, не привязан ли уже этот кошелек
        existing_wallet = crud.get_wallet_by_address(db, address)
        if existing_wallet:
            if existing_wallet.user_id != current_user.id:
                raise HTTPException(
                    status_code=400,
                    detail="Wallet already connected to another account"
                )
            return {"status": "success", "message": "Wallet already connected"}
        
        # Создаем новую привязку
        wallet = crud.create_wallet(db, current_user.id, address)
        
        return {"status": "success", "wallet": wallet.address}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance/{address}")
async def get_wallet_balance(
    address: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получаем баланс кошелька из блокчейна"""
    try:
        # Проверяем что кошелек принадлежит пользователю
        wallet = crud.get_wallet_by_address(db, address)
        if not wallet or wallet.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        balance = await ton_service.get_wallet_balance(address)
        return {"balance": balance}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deposit/verify")
async def verify_deposit(
    deposit_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Проверяем и обрабатываем депозит"""
    try:
        tx_hash = deposit_data.get("tx_hash")
        address = deposit_data.get("address")
        amount = deposit_data.get("amount")
        
        if not all([tx_hash, address, amount]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Проверяем что кошелек принадлежит пользователю
        wallet = crud.get_wallet_by_address(db, address)
        if not wallet or wallet.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Проверяем транзакцию в блокчейне
        is_verified = await ton_service.verify_transaction(tx_hash, address, amount)
        if not is_verified:
            raise HTTPException(status_code=400, detail="Transaction verification failed")
        
        # Проверяем не обрабатывали ли уже эту транзакцию
        existing_tx = crud.get_transaction_by_hash(db, tx_hash)
        if existing_tx:
            raise HTTPException(status_code=400, detail="Transaction already processed")
        
        # Создаем запись о транзакции
        transaction = crud.create_transaction(db, wallet.id, tx_hash, amount, "deposit")
        
        # Зачисляем средства на баланс пользователя
        user = crud.update_user_balance(db, current_user.telegram_id, "ton", amount)
        
        # Обновляем статус транзакции
        crud.update_transaction_status(db, tx_hash, "completed")
        
        return {
            "status": "success",
            "amount": amount,
            "new_balance": user.ton_balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw")
async def create_withdrawal(
    withdrawal_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Создаем запрос на вывод средств"""
    try:
        amount = withdrawal_data.get("amount")
        address = withdrawal_data.get("address")
        
        if not all([amount, address]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Проверяем достаточно ли средств
        if current_user.ton_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Получаем кошелек пользователя
        wallet = crud.get_wallet_by_user(db, current_user.id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Отправляем транзакцию
        tx_hash = await ton_service.send_transaction(wallet.address, address, amount)
        if not tx_hash:
            raise HTTPException(status_code=500, detail="Failed to send transaction")
        
        # Создаем запись о транзакции
        transaction = crud.create_transaction(db, wallet.id, tx_hash, amount, "withdrawal")
        
        # Списываем средства
        user = crud.update_user_balance(db, current_user.telegram_id, "ton", -amount)
        
        return {
            "status": "pending",
            "tx_hash": tx_hash,
            "amount": amount,
            "new_balance": user.ton_balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions")
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получаем историю транзакций"""
    try:
        wallets = crud.get_user_wallets(db, current_user.id)
        transactions = []
        for wallet in wallets:
            transactions.extend(wallet.transactions)
        
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        
        return {
            "transactions": [
                {
                    "id": tx.id,
                    "tx_hash": tx.tx_hash,
                    "amount": float(tx.amount),
                    "type": tx.transaction_type,
                    "status": tx.status,
                    "created_at": tx.created_at.isoformat(),
                    "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
                }
                for tx in transactions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))