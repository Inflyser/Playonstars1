import asyncio
import json
import logging
import time
from typing import Dict, Set
from fastapi import WebSocket
from datetime import datetime 

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.crash_game_connections: Set[WebSocket] = set()
        self.connection_timestamps: Dict[WebSocket, float] = {}  # ✅ Таймстампы соединений
        self.crash_game = None  # ✅ Будет установлен извне
        
            
    async def _broadcast_to_crash_game(self, message: str):
        """Приватный метод для broadcast сообщений только к подключениям crash игры"""
        if not self.crash_game_connections:
            return

    def set_crash_game(self, crash_game):
        """Устанавливаем ссылку на crash game"""
        self.crash_game = crash_game

    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        self.connection_timestamps[websocket] = time.time()
        logger.info(f"Client connected to channel '{channel}'. Total: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        
        if websocket in self.connection_timestamps:
            del self.connection_timestamps[websocket]
        
        logger.info(f"Client disconnected from channel '{channel}'")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            
            
    async def send_crash_update(self, data: dict):
        """Отправка обновлений игры"""
        message = {
            "type": "crash_update",
            "data": data
        }
        await self.broadcast_crash_game(message)  # ✅ Исправлено
    
    async def send_crash_result(self, data: dict):
        """Отправка результатов игры"""
        message = {
            "type": "crash_result", 
            "data": data
        }
        await self.broadcast_crash_game(message)

    async def broadcast(self, message: dict, channel: str = "general"):
        if channel in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[channel]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.add(websocket)
            
            # Удаляем отключенные соединения
            for websocket in disconnected:
                self.disconnect(websocket, channel)
    
    async def handle_crash_bet(self, websocket: WebSocket, data: dict):
        """Обработка ставок в краш-игре"""
        try:
            print(f"🎯 [WebSocket] Received bet data: {data}")
            
            user_id = data.get("user_id")
            amount = data.get("amount")
            auto_cashout = data.get("auto_cashout")
            
            if not all([user_id, amount]):
                print("❌ [WebSocket] Missing required fields")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "error",
                    "message": "Missing required fields"
                }, websocket)
                return
            
            if not self.crash_game:
                print("❌ [WebSocket] Crash game not initialized")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "error", 
                    "message": "Game not ready"
                }, websocket)
                return
            
            # ✅ Сохраняем ставку в БД
            print(f"🎯 [WebSocket] Calling place_bet for user {user_id}, amount {amount}")
            success = await self.crash_game.place_bet(int(user_id), float(amount), auto_cashout)
            
            if success:
                print(f"✅ [WebSocket] Bet successfully processed for user {user_id}")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "success",
                    "amount": amount
                }, websocket)
                
                # ✅ Рассылаем обновление о новой ставке всем
                await self.broadcast_crash_game({
                    "type": "new_bet",
                    "data": {
                        "user_id": user_id,
                        "amount": amount,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            else:
                print(f"❌ [WebSocket] Failed to process bet for user {user_id}")
                await self.send_personal_message({
                    "type": "bet_placed", 
                    "status": "error",
                    "message": "Failed to place bet"
                }, websocket)
                
        except Exception as e:
            print(f"❌ [WebSocket] Error handling bet: {e}")
            await self.send_personal_message({
                "type": "bet_placed",
                "status": "error", 
                "message": str(e)
            }, websocket)
    
    async def cash_out(self, user_id: int):
        """Обработка вывода средств"""
        try:
            if not self.crash_game:
                return False
            
            success = await self.crash_game.cash_out(user_id)
            if success:
                await self.broadcast_crash_game({
                    "type": "cash_out",
                    "data": {
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            return success
            
        except Exception as e:
            print(f"❌ [WebSocket] Error handling cash out: {e}")
            return False

    # Специальные методы для краш-игры
    async def connect_crash_game(self, websocket: WebSocket):
        await websocket.accept()
        
        # ✅ Очищаем мертвые соединения перед добавлением
        await self.clean_dead_connections()
        
        self.crash_game_connections.add(websocket)
        self.connection_timestamps[websocket] = time.time()
        
        logger.info(f"✅ Client connected to crash game. Total: {len(self.crash_game_connections)}")
        print(f"📊 Active connections: {[id(ws) for ws in self.crash_game_connections]}")

    def disconnect_crash_game(self, websocket: WebSocket):
        if websocket in self.crash_game_connections:
            self.crash_game_connections.discard(websocket)
        if websocket in self.connection_timestamps:
            del self.connection_timestamps[websocket]
        
        logger.info(f"🔌 Client disconnected from crash game. Total: {len(self.crash_game_connections)}")

    async def broadcast_crash_game(self, message: dict):
        """Трансляция сообщений для краш-игры"""
        disconnected = set()
        for websocket in self.crash_game_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to crash game client: {e}")
                disconnected.add(websocket)
        
        for websocket in disconnected:
            self.disconnect_crash_game(websocket)

    async def send_crash_update(self, data: dict):
        """Отправляем обновление состояния краш-игры"""
        await self.broadcast_crash_game({
            "type": "crash_update",
            "data": data
        })

    async def send_crash_result(self, data: dict):
        """Отправляем результат краш-игры"""
        await self.broadcast_crash_game({
            "type": "crash_result", 
            "data": data
        })

    async def send_bet_update(self, bet_data: dict):
        """Отправляем обновление о новой ставке"""
        await self.broadcast_crash_game({
            "type": "new_bet",
            "data": bet_data
        })

    async def handle_crash_bet(self, websocket: WebSocket, data: dict):
        """Обработка ставок в краш-игре"""
        try:
            print(f"🎯 [WebSocket] Received bet data: {data}")
            
            user_id = data.get("user_id")
            amount = data.get("amount")
            auto_cashout = data.get("auto_cashout")
            
            # Обновляем таймстамп активности
            self.connection_timestamps[websocket] = time.time()
            
            if not all([user_id, amount]):
                print("❌ [WebSocket] Missing required fields")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "error",
                    "message": "Missing required fields"
                }, websocket)
                return
            
            # ✅ Проверяем, что crash_game установлен
            if not self.crash_game:
                print("❌ [WebSocket] Crash game not initialized")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "error", 
                    "message": "Game not ready"
                }, websocket)
                return
            
            # ✅ Сохраняем ставку в БД
            print(f"🎯 [WebSocket] Calling place_bet for user {user_id}, amount {amount}")
            success = await self.crash_game.place_bet(int(user_id), float(amount), auto_cashout)
            
            if success:
                print(f"✅ [WebSocket] Bet successfully processed for user {user_id}")
                await self.send_personal_message({
                    "type": "bet_placed",
                    "status": "success",
                    "amount": amount
                }, websocket)
                
                # ✅ Рассылаем обновление о новой ставке всем
                await self.send_bet_update({
                    "user_id": user_id,
                    "amount": amount,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                print(f"❌ [WebSocket] Failed to process bet for user {user_id}")
                await self.send_personal_message({
                    "type": "bet_placed", 
                    "status": "error",
                    "message": "Failed to place bet"
                }, websocket)
                
        except Exception as e:
            print(f"❌ [WebSocket] Error handling bet: {e}")
            await self.send_personal_message({
                "type": "bet_placed",
                "status": "error", 
                "message": str(e)
            }, websocket)
            
    async def send_crash_update(self, data: dict):
        """Отправка обновлений игры с настройками"""
        message = {
            "type": "crash_update",
            "data": data
        }
        await self._broadcast_to_crash_game(json.dumps(message))

    async def clean_dead_connections(self):
        """Очищаем неактивные соединения"""
        current_time = time.time()
        dead_connections = []
        
        for websocket in list(self.crash_game_connections):
            # Проверяем соединения, которые неактивны более 60 секунд
            if websocket in self.connection_timestamps:
                last_active = self.connection_timestamps[websocket]
                if current_time - last_active > 60:
                    dead_connections.append(websocket)
            else:
                dead_connections.append(websocket)
        
        # Удаляем мертвые соединения
        for websocket in dead_connections:
            self.disconnect_crash_game(websocket)
            
        if dead_connections:
            print(f"🧹 Removed {len(dead_connections)} dead connections")

    async def check_connection_health(self):
        """Периодическая проверка здоровья соединений"""
        while True:
            await asyncio.sleep(30)  # Проверяем каждые 30 секунд
            await self.clean_dead_connections()

# Глобальный экземпляр менеджера
websocket_manager = WebSocketManager()