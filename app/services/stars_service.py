import requests
import logging
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)

class StarsService:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
    
    async def create_invoice(self, user_id: int, amount: int) -> Optional[str]:
        """Создание инвойса для Stars"""
        try:
            payload = {
                "title": "PlayOnStars - Пополнение баланса",
                "description": f"Пополнение на {amount} STARS",
                "payload": f"user_{user_id}_{amount}",
                "provider_token": "",
                "currency": "XTR",
                "prices": [{"label": f"{amount} STARS", "amount": amount * 100}]
            }
            
            response = requests.post(
                f"{self.api_url}/createInvoiceLink",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data['result']
            return None
                
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None

# Создаем экземпляр сервиса
stars_service = StarsService()