import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.crash_game_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to channel '{channel}'. Total: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info(f"Client disconnected from channel '{channel}'")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

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

    # Специальные методы для краш-игры
    async def connect_crash_game(self, websocket: WebSocket):
        await websocket.accept()
        self.crash_game_connections.add(websocket)
        logger.info(f"Client connected to crash game. Total: {len(self.crash_game_connections)}")

    def disconnect_crash_game(self, websocket: WebSocket):
        self.crash_game_connections.discard(websocket)
        logger.info("Client disconnected from crash game")

    async def broadcast_crash_game(self, message: dict):
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
        await self.broadcast_crash_game({
            "type": "crash_update",
            "data": data
        })

    async def send_crash_result(self, data: dict):
        await self.broadcast_crash_game({
            "type": "crash_result", 
            "data": data
        })

# Глобальный экземпляр менеджера
websocket_manager = WebSocketManager()