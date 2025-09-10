from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.websocket_manager import websocket_manager
from app.database.session import get_db
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ✅ УДАЛИТЬ дублирующий endpoint /ws - оставить только /ws/general
@router.websocket("/ws/general")
async def websocket_general(websocket: WebSocket, db: Session = Depends(get_db)):
    """Общее WebSocket подключение для всех клиентов"""
    await websocket.accept()
    await websocket_manager.connect(websocket, "general")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"📨 General WebSocket message: {message}")
                
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                
    except WebSocketDisconnect:
        logger.info("🔌 General WebSocket disconnected")
        websocket_manager.disconnect(websocket, "general")
    except Exception as e:
        logger.error(f"❌ General WebSocket error: {e}")
        websocket_manager.disconnect(websocket, "general")

@router.websocket("/ws/crash")
async def websocket_crash(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint specifically for crash game"""
    await websocket.accept()
    await websocket_manager.connect_crash_game(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"🎮 Crash WebSocket message: {message}")
                
                if message.get("type") == "place_bet":
                    logger.info("🎯 Processing bet placement")
                    await websocket_manager.handle_crash_bet(websocket, message)
                    
                elif message.get("type") == "cash_out":
                    logger.info("💵 Processing cash out")
                    # Добавьте обработку cash_out
                    user_id = message.get("user_id")
                    if user_id:
                        await websocket_manager.cash_out(user_id)
                    
                elif message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                    
                else:
                    logger.warning(f"❓ Unknown message type: {message.get('type')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info("🔌 Crash WebSocket disconnected")
        websocket_manager.disconnect_crash_game(websocket)
    except Exception as e:
        logger.error(f"❌ Crash WebSocket error: {e}")
        websocket_manager.disconnect_crash_game(websocket)

@router.websocket("/ws/user/{user_id}")
async def websocket_user(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """Персональные WebSocket соединения для пользователей"""
    await websocket.accept()
    channel_name = f"user_{user_id}"
    await websocket_manager.connect(websocket, channel_name)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"👤 User {user_id} WebSocket message: {message}")
                
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error for user {user_id}: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"🔌 User {user_id} WebSocket disconnected")
        websocket_manager.disconnect(websocket, channel_name)
    except Exception as e:
        logger.error(f"❌ User WebSocket error: {e}")
        websocket_manager.disconnect(websocket, channel_name)

# ✅ Добавим health check endpoint для WebSocket
@router.get("/ws/health")
async def websocket_health():
    """Проверка статуса WebSocket соединений"""
    return {
        "status": "healthy",
        "general_connections": len(websocket_manager.active_connections.get("general", [])),
        "crash_connections": len(websocket_manager.crash_game_connections),
        "total_connections": sum(len(conns) for conns in websocket_manager.active_connections.values()) + len(websocket_manager.crash_game_connections)
    }

# ✅ Добавим endpoint для отправки тестового сообщения
@router.post("/ws/test-message")
async def send_test_message(message: dict):
    """Отправка тестового сообщения во все crash соединения"""
    try:
        await websocket_manager.broadcast_crash_game({
            "type": "test_message",
            "data": message,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        return {"status": "success", "message": "Test message sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}