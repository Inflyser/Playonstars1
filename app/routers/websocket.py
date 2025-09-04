from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.websocket_manager import websocket_manager
from app.database.session import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.websocket("/api/ws/general")
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

@router.websocket("/api/ws/crash")
async def websocket_crash(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect_crash_game(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка ставок в краш-игре
            try:
                message = json.loads(data)
                if message.get("type") == "place_bet":
                    # Здесь логика обработки ставки
                    pass
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect_crash_game(websocket)

@router.websocket("/api/ws/user/{user_id}")
async def websocket_user(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket, f"user_{user_id}")
    try:
        while True:
            data = await websocket.receive_text()
            # Персональные сообщения для пользователя
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, f"user_{user_id}")