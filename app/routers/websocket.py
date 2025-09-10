from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.websocket_manager import websocket_manager
from app.database.session import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """Основной WebSocket endpoint для общего подключения"""
    await websocket_manager.connect(websocket, "general")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Обрабатываем ping/pong
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong", 
                        "timestamp": message.get("timestamp")
                    })
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "general")
        
        
@router.websocket("/ws/general")
async def websocket_general(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket, "general")
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка входящих сообщений
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, websocket)
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "general")
        
        
        

@router.websocket("/ws/user/{user_id}")
async def websocket_user(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket, f"user_{user_id}")
    try:
        while True:
            data = await websocket.receive_text()
            # Персональные сообщения для пользователя
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, f"user_{user_id}")
        
        

        
@router.websocket("/ws/crash")
async def websocket_crash(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect_crash_game(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message.get("type") == "place_bet":
                    print("🎯 Processing bet placement")
                    await websocket_manager.handle_crash_bet(websocket, message)
                    
                elif message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                
    except WebSocketDisconnect:
        websocket_manager.disconnect_crash_game(websocket)
        



@router.websocket("/ws/test")
async def websocket_test():
    return {
        "websocket_enabled": True,
        "crash_connections": len(websocket_manager.crash_game_connections),
        "allowed_origins": [
            "https://playonstars.netlify.app",
            "https://web.telegram.org"
        ]
    }