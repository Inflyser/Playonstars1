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
            webhook_url = f"{os.getenv('WEBHOOK_URL_TON', '').rstrip('/')}/api/webhook/ton"
            print(f"🔗 Registering TON webhook: {webhook_url}")
            
            # ✅ Используем правильный endpoint для TON API v2
            url = f"{self.base_url}/webhook"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": webhook_url,
                "subscription_type": "account",
                "subscription_filter": {
                    "account": self.wallet_address,
                    "transaction_types": ["in"]
                },
                "secret": self.webhook_secret
            }
            
            print(f"📤 Sending TON webhook registration to: {url}")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print("✅ TON Webhook successfully registered")
                return True
            else:
                print(f"❌ TON Webhook registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error setting up TON webhook: {e}")
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
            print(f"Error processing TON webhook: {e}")
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
    
    async def check_deposits_to_wallet(self) -> list:
        """Проверяем все транзакции на кошелек приложения (fallback)"""
        try:
            url = f"{self.base_url}/blockchain/accounts/{self.wallet_address}/transactions"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(url, headers=headers, params={'limit': 50})
            if response.status_code == 200:
                transactions = response.json().get('transactions', [])
                
                deposits = []
                for tx in transactions:
                    in_msg = tx.get('in_msg')
                    if in_msg and in_msg.get('destination') == self.wallet_address:
                        deposits.append({
                            'tx_hash': tx.get('hash'),
                            'from_address': in_msg.get('source'),
                            'amount': float(in_msg.get('value', 0)) / 1e9,
                            'timestamp': tx.get('utime')
                        })
                
                return deposits
            return []
        except Exception as e:
            print(f"Error checking deposits: {e}")
            return []

ton_service = TonService()