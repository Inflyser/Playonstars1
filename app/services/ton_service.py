import os
import requests
import hmac
import hashlib
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud

class TonService:
    def __init__(self):
        self.api_key = os.getenv('TON_API_KEY', '')
        self.wallet_address = os.getenv('TON_WALLET_ADDRESS', '')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', os.urandom(24).hex())
        self.base_url = "https://tonapi.io/v2"
    
    async def setup_webhook(self):
        """Настраиваем веб-перехватчик для уведомлений о транзакциях"""
        try:
            webhook_url = f"{os.getenv('WEBHOOK_URL_TON', '')}/api/webhook/ton"
            
            # Регистрируем веб-перехватчик для отслеживания транзакций
            url = f"{self.base_url}/webhooks/account"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": webhook_url,
                "account": self.wallet_address,
                "types": ["transaction"],
                "secret": self.webhook_secret
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print("✅ Webhook successfully registered")
                return True
            else:
                print(f"❌ Webhook registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error setting up webhook: {e}")
            return False
    
    def verify_webhook_signature(self, request: Request, payload: bytes) -> bool:
        """Проверяем подпись веб-перехватчика"""
        try:
            signature = request.headers.get('X-TonAPI-Signature', '')
            computed_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, computed_signature)
        except Exception:
            return False
    
    async def process_webhook(self, request: Request, payload: dict):
        """Обрабатываем входящий веб-перехватчик"""
        try:
            # Проверяем подпись
            body_bytes = await request.body()
            if not self.verify_webhook_signature(request, body_bytes):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            event_type = payload.get('type')
            data = payload.get('data', {})
            
            if event_type == 'transaction':
                await self.handle_transaction_event(data)
            
            return {"status": "processed"}
            
        except Exception as e:
            print(f"Error processing webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_transaction_event(self, transaction_data: dict):
        """Обрабатываем событие транзакции"""
        try:
            db = SessionLocal()
            
            tx_hash = transaction_data.get('hash')
            in_msg = transaction_data.get('in_msg', {})
            
            # Проверяем что это входящая транзакция на наш кошелек
            if (in_msg.get('destination') == self.wallet_address and 
                in_msg.get('source') != self.wallet_address):
                
                amount = float(in_msg.get('value', 0)) / 1e9  # нанотоны → TON
                from_address = in_msg.get('source', '')
                
                # Ищем кошелек отправителя в нашей базе
                sender_wallet = crud.get_wallet_by_address(db, from_address)
                
                if sender_wallet:
                    # Проверяем не обрабатывали ли уже эту транзакцию
                    existing_tx = crud.get_transaction_by_hash(db, tx_hash)
                    if not existing_tx:
                        # Создаем запись о транзакции
                        transaction = crud.create_transaction(
                            db, 
                            sender_wallet.id, 
                            tx_hash, 
                            amount, 
                            "deposit"
                        )
                        
                        # Зачисляем средства на баланс пользователя
                        user = crud.update_user_balance(
                            db, 
                            sender_wallet.user.telegram_id, 
                            "ton", 
                            amount
                        )
                        
                        # Обновляем статус транзакции
                        crud.update_transaction_status(db, tx_hash, "completed")
                        
                        print(f"✅ Processed deposit: {amount} TON from {from_address}")
            
            db.close()
            
        except Exception as e:
            print(f"Error handling transaction event: {e}")

    # Добавляем дополнительные методы для полноты функционала
    async def get_wallet_balance(self, address: str) -> float:
        """Получаем баланс кошелька"""
        try:
            url = f"{self.base_url}/accounts/{address}"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                balance = int(data.get('balance', 0)) / 1e9  # нанотоны → TON
                return balance
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0

    async def verify_transaction(self, tx_hash: str, to_address: str, amount: float) -> bool:
        """Проверяем транзакцию в блокчейне"""
        try:
            url = f"{self.base_url}/blockchain/transactions/{tx_hash}"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Проверяем что транзакция успешна
                if not data.get('success', False):
                    return False
                
                # Проверяем входящие сообщения
                in_msg = data.get('in_msg')
                if in_msg:
                    destination = in_msg.get('destination', {}).get('address', '')
                    value = float(in_msg.get('value', 0)) / 1e9  # нанотоны → TON
                    
                    # Проверяем адрес и сумму
                    if destination.endswith(to_address.replace('EQ', '')) and value >= amount:
                        return True
                
                return False
            return False
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return False

ton_service = TonService()