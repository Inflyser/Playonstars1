from .telegram import router as telegram_router
from .websocket import router as websocket_router

# Добавьте если создаете wallet.py
from .wallet import router as wallet_router

__all__ = ['telegram_router', 'websocket_router', 'wallet_router']