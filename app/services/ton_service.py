import os
import requests
import hmac
import hashlib
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud
import aiohttp
from app.database.models import Wallet

class TonService:
    def __init__(self):
        self.api_key = os.getenv('TON_API_KEY', '')
        self.wallet_address = os.getenv('TON_WALLET_ADDRESS', '')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', os.urandom(24).hex())
        # ✅ ПРАВИЛЬНЫЙ БАЗОВЫЙ URL для TON API v2
        self.base_url = "https://tonapi.io/v2"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        
    async def check_deposits_to_wallet(self):
        """Проверяем депозиты на основной кошелек (для обратной совместимости)"""
        try:
            if not self.api_key or not self.wallet_address:
                print("⚠️ TON API key or wallet address not set")
                return []

            print(f"🔍 Checking deposits for main wallet: {self.wallet_address}")

            # Используем существующий метод
            transactions = await self.get_wallet_transactions(self.wallet_address)
            deposits = []

            for tx in transactions:
                # Логика обработки транзакций
                in_msg = tx.get('in_msg', {})
                if in_msg and in_msg.get('destination') == self.wallet_address:
                    deposits.append({
                        'tx_hash': tx.get('hash'),
                        'amount': float(in_msg.get('value', 0)) / 1e9,
                        'from_address': in_msg.get('source')
                    })

            return deposits

        except Exception as e:
            print(f"Error checking wallet deposits: {e}")
            return []
    
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
        """Проверяем доступность TON API - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            url = f"{self.base_url}/health"
            print(f"🌐 Checking TON API health: {url}")

            # Используем requests вместо aiohttp для простоты
            response = requests.get(url, headers=self.headers, timeout=10)

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


    async def check_deposits_to_user_wallets(self):
        """Проверяем депозиты на все кошельки пользователей"""
        try:
            db = SessionLocal()

            # Получаем все кошельки пользователей
            user_wallets = db.query(Wallet).all()

            for wallet in user_wallets:
                print(f"🔍 Checking deposits for wallet: {wallet.address}")

                # Получаем транзакции для этого кошелька
                transactions = await self.get_wallet_transactions(wallet.address)

                for tx in transactions:
                    await self.process_deposit_transaction(db, tx, wallet)

            db.close()

        except Exception as e:
            print(f"Error checking user wallet deposits: {e}")
            if 'db' in locals():
                db.close()       


    async def get_wallet_transactions(self, wallet_address: str):
        """Получаем транзакции кошелька через TON API"""
        try:
            url = f"{self.base_url}/accounts/{wallet_address}/transactions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('transactions', [])
            else:
                print(f"TON API transactions error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []



    async def process_deposit_transaction(self, db: Session, tx_data: dict, wallet: Wallet):
        """Обрабатываем депозитную транзакцию"""
        try:
            tx_hash = tx_data.get('hash')

            # Проверяем не обрабатывали ли уже эту транзакцию
            existing_tx = crud.get_transaction_by_hash(db, tx_hash)
            if existing_tx:
                return

            # Ищем входящие сообщения (депозиты)
            in_msg = tx_data.get('in_msg')
            if in_msg and in_msg.get('destination') == wallet.address:
                value = in_msg.get('value', 0)
                amount = float(value) / 1e9  # нанотоны → TON

                if amount > 0:
                    # Создаем запись о транзакции
                    transaction = crud.create_transaction(
                        db, 
                        wallet.id, 
                        tx_hash, 
                        amount, 
                        "deposit"
                    )

                    # Зачисляем средства на баланс пользователя
                    user = crud.update_user_balance(
                        db, 
                        wallet.user.telegram_id, 
                        "ton", 
                        amount
                    )

                    # Обновляем статус транзакции
                    crud.update_transaction_status(db, tx_hash, "completed")

                    print(f"✅ Processed deposit: {amount} TON to {wallet.user.telegram_id}")

        except Exception as e:
            print(f"Error processing deposit transaction: {e}")

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

    async def get_wallet_transactions(self, wallet_address: str, limit: int = 100):
        """Получаем транзакции кошелька через TON API"""
        try:
            if not self.api_key:
                print("⚠️ TON API key not set")
                return []
            
            url = f"{self.base_url}/accounts/{wallet_address}/transactions"
            params = {'limit': limit}
            
            print(f"🌐 Fetching transactions for: {wallet_address}")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('transactions', [])
            else:
                print(f"❌ TON API transactions error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting transactions: {e}")
            return []

    async def handle_transaction_event(self, transaction_data: dict):
        """Обрабатываем событие транзакции - ТЕПЕРЬ ПРАВИЛЬНО"""
        try:
            db = SessionLocal()

            print(f"📊 Transaction data: {transaction_data}")

            # Ищем информацию о транзакции
            tx_hash = transaction_data.get('hash') or transaction_data.get('transaction_id')
            in_msg = transaction_data.get('in_msg') or transaction_data.get('message', {})

            destination = in_msg.get('destination') or in_msg.get('to')
            value = in_msg.get('value') or in_msg.get('amount', 0)

            if destination and value:
                amount = float(value) / 1e9

                # Ищем кошелек получателя в нашей базе
                recipient_wallet = crud.get_wallet_by_address(db, destination)

                if recipient_wallet:
                    # Проверяем не обрабатывали ли уже эту транзакцию
                    existing_tx = crud.get_transaction_by_hash(db, tx_hash)
                    if not existing_tx:
                        # Создаем запись о транзакции
                        transaction = crud.create_transaction(
                            db, 
                            recipient_wallet.id, 
                            tx_hash, 
                            amount, 
                            "deposit"
                        )

                        # Зачисляем средства на баланс пользователя
                        user = crud.update_user_balance(
                            db, 
                            recipient_wallet.user.telegram_id, 
                            "ton", 
                            amount
                        )

                        # Обновляем статус транзакции
                        crud.update_transaction_status(db, tx_hash, "completed")

                        print(f"✅ Processed deposit: {amount} TON to user {recipient_wallet.user.telegram_id}")
                else:
                    print(f"⚠️ Unknown recipient wallet: {destination}")

            db.close()

        except Exception as e:
            print(f"Error handling transaction event: {e}")
            if 'db' in locals():
                db.close()

                
                
    

ton_service = TonService()


