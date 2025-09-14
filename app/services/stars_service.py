import requests
import logging
from typing import Optional, Dict
import os
import json

logger = logging.getLogger(__name__)

class StarsService:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
    
    async def create_invoice(self, user_id: int, amount: int) -> Optional[str]:
        """Создание инвойса для Stars"""
        try:
            # ✅ ПРАВИЛЬНЫЙ формат для Stars
            payload = {
                "title": "PlayOnStars - Пополнение баланса",
                "description": f"Пополнение на {amount} STARS",
                "payload": f"stars_deposit:{user_id}:{amount}",  # ✅ Простая строка
                "provider_token": "",  # ✅ Для Stars оставляем пустым
                "currency": "XTR",     # ✅ Валюта Telegram Stars
                "prices": [{"label": f"{amount} STARS", "amount": amount}]  # ✅ Без умножения на 100
            }
            
            response = requests.post(
                f"{self.api_url}/createInvoiceLink",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data['result']
            else:
                logger.error(f"Telegram API error: {data.get('description')}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None

# Создаем экземпляр сервиса
stars_service = StarsService()