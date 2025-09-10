import os
import random
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud
from datetime import datetime
import asyncio

class MockTonService:
    def __init__(self):
        self.mock_wallet_address = "EQmock_wallet_address_for_testing_123456789"
        self.mock_transactions = {}
        self.pending_deposits = {}
    
    async def setup_webhook(self):
        """Mock вебхука - всегда успешно"""
        print("✅ Mock TON webhook setup - always successful")
        return True
    
    async def check_ton_api_status(self):
        """Mock статуса API"""
        return True
    
    async def get_wallet_balance(self, wallet_address: str) -> float:
        """Mock баланса кошелька"""
        # Для тестов возвращаем случайный баланс
        return round(random.uniform(0.5, 10.0), 2)
    
    async def process_webhook(self, request: Request, payload: dict):
        """Mock обработки вебхука"""
        print(f"📨 Mock webhook received: {payload}")
        return {"status": "processed", "mock": True}
    
    async def simulate_deposit(self, user_telegram_id: int, amount: float):
        """Симулируем депозит для тестирования"""
        db = SessionLocal()
        try:
            user = crud.get_user_by_telegram_id(db, user_telegram_id)
            if not user:
                print(f"❌ User {user_telegram_id} not found")
                return False
            
            # Находим или создаем кошелек пользователя
            wallet = crud.get_wallet_by_user(db, user.id)
            if not wallet:
                print(f"❌ Wallet not found for user {user_telegram_id}")
                return False
            
            # Генерируем mock хэш транзакции
            tx_hash = f"mock_tx_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
            
            # Создаем транзакцию
            transaction = crud.create_transaction(
                db=db,
                wallet_id=wallet.id,
                tx_hash=tx_hash,
                amount=amount,
                transaction_type="deposit"
            )
            
            # Обновляем баланс пользователя
            user = crud.update_user_balance(db, user_telegram_id, "ton", amount)
            
            # Обновляем статус транзакции
            crud.update_transaction_status(db, tx_hash, "completed")
            
            print(f"✅ Mock deposit processed: {amount} TON for user {user_telegram_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error in mock deposit: {e}")
            return False
        finally:
            db.close()
    
    async def simulate_game_bet(self, user_telegram_id: int, amount: float):
        """Симулируем ставку в игре"""
        db = SessionLocal()
        try:
            user = crud.get_user_by_telegram_id(db, user_telegram_id)
            if not user:
                return False
            
            # Проверяем достаточно ли баланса
            if user.stars_balance < amount:
                print(f"❌ Insufficient balance: {user.stars_balance} < {amount}")
                return False
            
            # Снимаем средства
            user.stars_balance -= amount
            db.commit()
            
            print(f"✅ Mock bet placed: {amount} stars by user {user_telegram_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error in mock bet: {e}")
            db.rollback()
            return False
        finally:
            db.close()

mock_ton_service = MockTonService()