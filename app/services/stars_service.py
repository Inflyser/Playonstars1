import requests
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class StarsService:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token:
            logger.error("BOT_TOKEN not set!")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def create_invoice(self, user_id: int, amount: int) -> Optional[str]:
        """Создание инвойса для Stars - ИСПРАВЛЕННАЯ версия"""
        try:
            # Умножаем amount на 100, потому что Telegram ожидает сумму в минимальных единицах (копейках)
            price_amount = amount

            # ✅ ПРАВИЛЬНЫЙ формат для Telegram Stars API
            payload = {
                "title": "PlayOnStars - Пополнение баланса",
                "description": f"Пополнение на {amount} STARS",
                "payload": f"stars_payment:{user_id}:{amount}",
                "currency": "XTR",  # ✅ Валюта Stars
                "prices": [{"label": f"{amount} STARS", "amount": price_amount}],
                "provider_token": "",  # ✅ Получаем из переменной окружения
                "need_name": False,
                "need_phone_number": False, 
                "need_email": False,
                "need_shipping_address": False
            }
            
            logger.info(f"Creating invoice with payload: {payload}")
            
            response = requests.post(
                f"{self.api_url}/createInvoiceLink",
                json=payload,
                timeout=30
            )
            
            logger.info(f"Telegram API response: {response.status_code}, {response.text}")
            
            data = response.json()
            
            if data.get('ok'):
                return data['result']
            else:
                error_msg = data.get('description', 'Unknown error')
                logger.error(f"Telegram API error: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return None

# Создаем экземпляр сервиса
stars_service = StarsService()