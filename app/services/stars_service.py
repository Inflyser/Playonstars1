import requests
import logging
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)

class StarsService:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token:
            logger.error("BOT_TOKEN not found in environment variables")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
    
    async def get_payment_status(self, payment_id: str) -> Optional[Dict]:
        """Получить статус платежа через Bot API"""
        if not self.bot_token:
            logger.error("BOT_TOKEN not configured")
            return None
            
        try:
            response = requests.get(
                f"{self.api_url}/getPaymentStatus",
                params={"payment_id": payment_id},
                timeout=10
            )
            data = response.json()
            
            if data.get('ok'):
                return data['result']
            else:
                logger.error(f"API error: {data.get('description')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return None
    
    async def refund_payment(self, payment_id: str) -> bool:
        """Возврат платежа (если потребуется)"""
        if not self.bot_token:
            return False
            
        try:
            response = requests.post(
                f"{self.api_url}/refundPayment",
                json={"payment_id": payment_id},
                timeout=10
            )
            data = response.json()
            return data.get('ok', False)
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            return False

# Создаем экземпляр сервиса
stars_service = StarsService()