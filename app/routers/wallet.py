from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.services.ton_service import ton_service
import logging
from datetime import datetime

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