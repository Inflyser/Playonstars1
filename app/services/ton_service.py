import os
import requests
from typing import Optional

class TonService:
    def __init__(self):
        self.manifest_url = f"{os.getenv('FRONTEND_URL', 'https://playonstars.netlify.app')}/tonconnect-manifest.json"
    
    async def get_wallet_balance(self, address: str) -> float:
        """Получаем баланс кошелька"""
        try:
            # Используем TON API для получения баланса
            url = f"https://tonapi.io/v2/accounts/{address}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                balance = int(data.get('balance', 0)) / 1e9  # Конвертируем нанотоны в TON
                return balance
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    async def verify_transaction(self, tx_hash: str, address: str, amount: float) -> bool:
        """Проверяем транзакцию в блокчейне"""
        try:
            url = f"https://tonapi.io/v2/blockchain/transactions/{tx_hash}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Проверяем что транзакция успешна и соответствует параметрам
                if (data.get('success', False) and 
                    data.get('in_msg', {}).get('destination') == address and
                    float(data.get('in_msg', {}).get('value', 0)) / 1e9 >= amount):
                    return True
            return False
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return False
    
    async def send_transaction(self, from_address: str, to_address: str, amount: float) -> Optional[str]:
        """Отправляем транзакцию (для вывода средств)"""
        try:
            # В реальном приложении здесь будет логика подписи транзакции
            # через TonConnect или другой кошелек
            return "simulated_tx_hash_for_development"
        except Exception as e:
            print(f"Error sending transaction: {e}")
            return None

ton_service = TonService()