from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.services.ton_service import ton_service
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from app.services.mock_ton_service import mock_ton_service

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
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        wallet_address = wallet_data.get("wallet_address")
        wallet_provider = wallet_data.get("wallet_provider", "tonconnect")
        network = wallet_data.get("network", "mainnet")
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address required")
        
        # Проверяем валидность TON адреса (базовая проверка)
        if not wallet_address.startswith(('EQ', 'UQ', '0Q')) or len(wallet_address) < 40:
            raise HTTPException(status_code=400, detail="Invalid TON address format")
        
        # Проверяем не привязан ли уже этот кошелек
        existing_wallet = crud.get_wallet_by_address(db, wallet_address)
        if existing_wallet:
            if existing_wallet.user_id != user.id:
                raise HTTPException(status_code=400, detail="Wallet already linked to another user")
            # Кошелек уже привязан к этому пользователю
            return {"status": "success", "wallet_id": existing_wallet.id, "message": "Wallet already linked"}
        
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
        
        logger.info(f"Wallet saved for user {user.id}: {wallet_address}")
        
        return {
            "status": "success", 
            "wallet_id": wallet.id,
            "message": "Wallet saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving wallet: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    """Получаем баланс кошелька через TON API"""
    try:
        # Базовая валидация адреса
        if not address or len(address) < 40:
            raise HTTPException(status_code=400, detail="Invalid wallet address")
        
        # Используем наш ton_service для получения баланса
        balance = await ton_service.get_wallet_balance(address)
        
        return {
            "address": address,
            "balance": balance,
            "currency": "TON",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting balance for {address}: {str(e)}")
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
        print(f"TON webhook error: {e}")
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
        raise HTTPException(status_code=404, detail="Transaction not found")
    
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
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = crud.get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
            "message": "Transaction created, waiting for confirmation"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/wallet/check-deposits")
async def check_user_deposits(
    request: Request,
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
      
      
# ТЕСТ


@router.post("/test/mock-deposit")
async def create_mock_deposit(
    request: Request,
    deposit_data: dict,
    db: Session = Depends(get_db)
):
    """Эндпоинт для создания тестового депозита"""
    if os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Only available in development")
    
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    amount = deposit_data.get("amount", 1.0)
    
    success = await mock_ton_service.simulate_deposit(telegram_id, amount)
    
    if success:
        return {
            "status": "success",
            "message": f"Mock deposit of {amount} TON processed",
            "mock": True
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to process mock deposit")

@router.post("/test/mock-bet")
async def create_mock_bet(
    request: Request,
    bet_data: dict,
    db: Session = Depends(get_db)
):
    """Эндпоинт для тестовой ставки"""
    if os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Only available in development")
    
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    amount = bet_data.get("amount", 10.0)
    
    success = await mock_ton_service.simulate_game_bet(telegram_id, amount)
    
    if success:
        return {
            "status": "success", 
            "message": f"Mock bet of {amount} stars placed",
            "mock": True
        }
    else:
        raise HTTPException(status_code=400, detail="Insufficient balance or other error")