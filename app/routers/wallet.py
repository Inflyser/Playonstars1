from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.services.ton_service import ton_service
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from app.database.models import Transaction

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/user/wallet")
async def save_user_wallet(
    request: Request,
    wallet_data: dict,
    db: Session = Depends(get_db)
):
    """Сохраняем адрес кошелька пользователя"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Не авторизован")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        wallet_address = wallet_data.get("wallet_address")
        wallet_provider = wallet_data.get("wallet_provider", "tonconnect")
        network = wallet_data.get("network", "mainnet")
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Адрес кошелька обязателен")
        
        # Проверяем валидность TON адреса (базовая проверка)
        if not wallet_address.startswith(('EQ', 'UQ', '0Q')) or len(wallet_address) < 40:
            raise HTTPException(status_code=400, detail="Неверный формат TON адреса")
        
        # Проверяем не привязан ли уже этот кошелек
        existing_wallet = crud.get_wallet_by_address(db, wallet_address)
        if existing_wallet:
            if existing_wallet.user_id != user.id:
                raise HTTPException(status_code=400, detail="Кошелек уже привязан к другому пользователю")
            # Кошелек уже привязан к этому пользователю
            return {"status": "success", "wallet_id": existing_wallet.id, "message": "Кошелек уже привязан"}
        
        # Создаем или обновляем кошелек
        wallet = crud.get_wallet_by_user(db, user.id)
        if wallet:
            wallet.address = wallet_address
            wallet.wallet_provider = wallet_provider
            wallet.is_verified = False
        else:
            wallet = crud.create_wallet(
                db, 
                user.id, 
                wallet_address, 
                wallet_provider
            )
        
        db.commit()
        
        logger.info(f"Кошелек сохранен для пользователя {user.id}: {wallet_address}")
        
        return {
            "status": "success", 
            "wallet_id": wallet.id,
            "message": "Кошелек успешно сохранен"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка сохранения кошелька: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    """Получаем баланс кошелька через TON API"""
    try:
        # Базовая валидация адреса
        if not address or len(address) < 40:
            raise HTTPException(status_code=400, detail="Неверный адрес кошелька")
        
        # Используем наш ton_service для получения баланса
        balance = await ton_service.get_wallet_balance(address)
        
        return {
            "address": address,
            "balance": balance,
            "currency": "TON",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения баланса для {address}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wallet/validate/{address}")
async def validate_wallet_address(address: str):
    """Проверяем валидность адреса кошелька"""
    try:
        # Простая валидация формата TON адреса
        is_valid = (
            address.startswith(('EQ', 'UQ', '0Q')) and 
            len(address) >= 40 and
            all(c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_' for c in address)
        )
        
        return {
            "address": address,
            "is_valid": is_valid,
            "format": "TON" if is_valid else "unknown"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/webhook/ton")
async def ton_webhook(request: Request):
    """Эндпоинт для получения веб-перехватчиков от TON API"""
    try:
        payload = await request.json()
        return await ton_service.process_webhook(request, payload)
    except Exception as e:
        print(f"Ошибка TON webhook: {e}")
        return {"status": "error", "message": str(e)}
    
@router.get("/ton/status")
async def ton_status():
    """Проверка статуса TON интеграции"""
    return {
        "ton_api_connected": bool(os.getenv("TON_API_KEY")),
        "wallet_address": os.getenv("TON_WALLET_ADDRESS"),
        "webhook_url": f"{os.getenv('WEBHOOK_URL_TON')}/api/webhook/ton",
        "has_wallet_secret": bool(os.getenv("TON_WALLET_SECRET"))
    }
    
@router.get("/wallet/transaction/{tx_hash}")
async def get_transaction_status(
    tx_hash: str,
    db: Session = Depends(get_db)
):
    """Проверяем статус транзакции"""
    transaction = crud.get_transaction_by_hash(db, tx_hash)
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    
    return {
        "tx_hash": transaction.tx_hash,
        "status": transaction.status,
        "amount": float(transaction.amount),
        "created_at": transaction.created_at.isoformat()
    }
    
@router.post("/wallet/deposit")
async def create_deposit(
    request: Request,
    deposit_data: dict,
    db: Session = Depends(get_db)
):
    """Создаем запись о депозите"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Не авторизован")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Создаем pending транзакцию
        transaction = crud.create_transaction(
            db=db,
            user_id=user.id,
            tx_hash=deposit_data.get("tx_hash"),
            amount=float(deposit_data.get("amount", 0)),
            transaction_type="deposit",
            status="pending"
        )
        
        return {
            "status": "success",
            "transaction_id": transaction.id,
            "message": "Транзакция создана, ожидание подтверждения"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/wallet/check-deposits")
async def check_user_deposits(
    request: Request,
    db: Session = Depends(get_db)
):
    """Проверяем депозиты пользователя - РАБОЧАЯ ВЕРСИЯ"""
    try:
        telegram_id = request.session.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=400, detail="Telegram ID required")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем кошелек пользователя
        wallet = crud.get_wallet_by_user(db, user.id)
        if not wallet:
            return {"pending_transactions": []}
        
        # Проверяем pending транзакции для этого кошелька
        pending_txs = db.query(Transaction).filter(
            Transaction.wallet_id == wallet.id,
            Transaction.status == "pending"
        ).all()
        
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
        
    except Exception as e:
        print(f"Error checking deposits: {e}")
        return {"pending_transactions": []}