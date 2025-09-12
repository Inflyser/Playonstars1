import os
import requests
import hmac
import hashlib
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud
import aiohttp

class TonService:
    def __init__(self):
        self.api_key = os.getenv('TON_API_KEY', '')
        self.wallet_address = os.getenv('TON_WALLET_ADDRESS', '')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', os.urandom(24).hex())
        # ✅ ПРАВИЛЬНЫЙ БАЗОВЫЙ URL для TON API v2
        self.base_url = "https://tonapi.io/v2"
    
    async def setup_webhook(self):
        """Настраиваем веб-перехватчик для TON API"""
        try:
            if not self.api_key or not self.wallet_address:
                print("⚠️ TON API key or wallet address not set - skipping webhook")
                return False
                
            webhook_url = f"{os.getenv('WEBHOOK_URL_TON')}/api/webhook/ton"
            print(f"🔗 Registering TON webhook: {webhook_url}")
            
            # ✅ ПРАВИЛЬНЫЙ endpoint для tonapi.io v2
            url = f"{self.base_url}/webhooks"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # ✅ ПРАВИЛЬНАЯ структура payload для tonapi.io v2
            payload = {
                "url": webhook_url,
                "subscription": {
                    "type": "Account",
                    "account": self.wallet_address
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print("✅ TON Webhook successfully registered")
                print(f"Webhook ID: {response.json().get('id')}")
                return True
            else:
                print(f"❌ TON Webhook failed: {response.status_code} - {response.text}")
                # Попробуем альтернативный подход
                return await self.try_alternative_webhook_setup(webhook_url)
                
        except Exception as e:
            print(f"Error setting up TON webhook: {e}")
            return False
    
    async def try_alternative_webhook_setup(self, webhook_url: str):
        """Альтернативный метод настройки вебхука"""
        try:
            # Альтернативный endpoint для старых версий API
            url = f"{self.base_url}/webhooks/token"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": webhook_url,
                "subscription_type": "account_transaction",
                "subscription_filter": {
                    "account": self.wallet_address
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print("✅ TON Webhook registered via alternative endpoint")
                return True
            else:
                print(f"❌ Alternative endpoint also failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error in alternative webhook setup: {e}")
            return False
    
    async def check_ton_api_status(self):
        """Проверяем статус TON API"""
        try:
            url = f"{self.base_url}/health"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print("✅ TON API is accessible and healthy")
                return True
            else:
                print(f"❌ TON API health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ TON API health check error: {e}")
            return False
    
    def verify_webhook_signature(self, request: Request, payload: bytes) -> bool:
        """Проверяем подпись веб-перехватчика"""
        try:
            signature = request.headers.get('X-TonAPI-Signature', '')
            if not signature:
                # В development режиме пропускаем проверку
                if os.getenv('ENVIRONMENT') == 'development':
                    return True
                return False
            
            computed_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, computed_signature)
        except Exception:
            return False
        
    # ton_service.py - добавь этот метод в класс TonService
    async def get_wallet_balance(self, wallet_address: str) -> float:
        """Получаем баланс кошелька через TON API"""
        try:
            print(f"🔍 Getting balance for wallet: {wallet_address}")
            
            if not self.api_key:
                print("⚠️ TON API key not set - returning 0")
                return 0.0
            
            # ✅ ПРАВИЛЬНЫЙ endpoint для получения информации о кошельке в tonapi.io v2
            url = f"{self.base_url}/accounts/{wallet_address}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            print(f"🌐 Making request to: {url}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ TON API response: {data}")
                
                # ✅ ПРАВИЛЬНЫЙ путь к балансу в tonapi.io v2
                balance_nano = data.get('balance', 0)
                balance_ton = int(balance_nano) / 1e9  # Конвертируем нанотоны в TON
                
                print(f"💰 Balance: {balance_ton} TON")
                return balance_ton
                
            else:
                print(f"❌ TON API error: {response.status_code} - {response.text}")
                return 0.0
                
        except Exception as e:
            print(f"❌ Error getting wallet balance: {e}")
            return 0.0
    
    async def process_webhook(self, request: Request, payload: dict):
        """Обрабатываем входящий веб-перехватчик"""
        try:
            # Проверяем подпись (только в production)
            if os.getenv('ENVIRONMENT') == 'production':
                body_bytes = await request.body()
                if not self.verify_webhook_signature(request, body_bytes):
                    print("❌ Invalid webhook signature")
                    raise HTTPException(status_code=401, detail="Invalid signature")
            
            event_type = payload.get('type')
            data = payload.get('data', {})
            
            print(f"📨 Received TON webhook event: {event_type}")
            
            if event_type == 'transaction':
                await self.handle_transaction_event(data)
            else:
                print(f"ℹ️ Unhandled event type: {event_type}")
            
            return {"status": "processed"}
            
        except Exception as e:
            print(f"Error processing TON webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        

    async def check_ton_api_status(self):
        """Проверяем доступность TON API"""
        try:
            url = f"{self.base_url}/v2/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"TON API health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"TON API health check error: {e}")
            return False
        
    
    async def handle_transaction_event(self, transaction_data: dict):
        """Обрабатываем событие транзакции"""
        try:
            db = SessionLocal()
            
            # Логируем полученные данные для отладки
            print(f"📊 Transaction data: {transaction_data}")
            
            # Извлекаем данные в зависимости от структуры API
            tx_hash = transaction_data.get('hash') or transaction_data.get('transaction_id')
            
            # Ищем информацию о входящем сообщении
            in_msg = None
            if 'in_msg' in transaction_data:
                in_msg = transaction_data['in_msg']
            elif 'message' in transaction_data:
                in_msg = transaction_data['message']
            
            if in_msg and tx_hash:
                destination = in_msg.get('destination') or in_msg.get('to')
                source = in_msg.get('source') or in_msg.get('from')
                value = in_msg.get('value') or in_msg.get('amount')
                
                # Проверяем что это входящая транзакция на наш кошелек
                if destination and destination == self.wallet_address and source != self.wallet_address:
                    
                    amount = float(value or 0) / 1e9  # нанотоны → TON
                    from_address = source
                    
                    print(f"💰 Incoming transaction: {amount} TON from {from_address}")
                    
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
                    else:
                        print(f"⚠️ Unknown sender wallet: {from_address}")
            
            db.close()
            
        except Exception as e:
            print(f"Error handling transaction event: {e}")
            if 'db' in locals():
                db.close()
                
                
                
    

ton_service = TonService()


