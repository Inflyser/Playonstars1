from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

@router.post("/telegram-stars/create-invoice")
async def create_stars_invoice(invoice_data: dict):
    """Создаем инвойс для оплаты через Telegram Stars"""
    try:
        # Вызываем Telegram Bot API для создания инвойса
        response = requests.post(
            "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/createInvoiceLink",
            json={
                "title": "Пополнение Stars",
                "description": f"Пополнение баланса на {invoice_data['amount']} Stars",
                "payload": f"user_{invoice_data['user_id']}",
                "provider_token": "<YOUR_PROVIDER_TOKEN>",
                "currency": "XTR",
                "prices": [{"label": "Stars", "amount": invoice_data['stars_amount'] * 100}],
                "max_tip_amount": 10000,
                "suggested_tip_amounts": [1000, 2000, 3000, 4000]
            }
        )
        
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/telegram-stars/webhook")
# async def stars_webhook(update: dict):
#     """Webhook для получения подтверждений платежей от Telegram"""
#     try:
#         if 'pre_checkout_query' in update:
#             # Подтверждаем платеж
#             user_id = update['pre_checkout_query']['from']['id']
#             amount = update['pre_checkout_query']['total_amount'] / 100
            
#             # Зачисляем звезды пользователю
#             await credit_user_stars(user_id, amount)
            
#             return {"ok": True}
            
#     except Exception as e:
#         print(f"Webhook error: {e}")
#         return {"ok": False}