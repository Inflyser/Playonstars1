import asyncio
import random
import math
from typing import Dict, List
from datetime import datetime
from app.services.websocket_manager import WebSocketManager

class CrashGame:
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.current_multiplier = 1.0
        self.is_playing = False
        self.bets: Dict[int, Dict] = {}  # user_id -> bet_data
        self.game_history: List[Dict] = []
        self.game_id = 0

    async def run_game_cycle(self):
        """Запуск цикла игры"""
        self.game_id += 1
        self.is_playing = True
        self.bets.clear()
        
        # Фаза приема ставок
        await self.ws_manager.send_crash_update({
            "game_id": self.game_id,
            "phase": "betting",
            "time_remaining": 15
        })
        
        for i in range(15, 0, -1):
            await asyncio.sleep(1)
            if not self.is_playing:
                return
                
            await self.ws_manager.send_crash_update({
                "game_id": self.game_id,
                "phase": "betting",
                "time_remaining": i
            })

        # Генерируем множитель
        multiplier = self.generate_multiplier()
        
        # Фаза полета
        await self.ws_manager.send_crash_update({
            "game_id": self.game_id,
            "phase": "flying",
            "multiplier": 1.0
        })
        
        current_multiplier = 1.0
        while current_multiplier < multiplier and self.is_playing:
            await asyncio.sleep(0.1)
            current_multiplier += 0.01
            current_multiplier = round(current_multiplier, 2)
            
            await self.ws_manager.send_crash_update({
                "game_id": self.game_id,
                "phase": "flying",
                "multiplier": current_multiplier
            })

        # Крах - игра окончена
        self.is_playing = False
        await self.ws_manager.send_crash_result({
            "game_id": self.game_id,
            "final_multiplier": multiplier,
            "crashed_at": multiplier,
            "timestamp": datetime.now().isoformat()
        })

        # Сохраняем в историю
        self.game_history.append({
            "game_id": self.game_id,
            "multiplier": multiplier,
            "timestamp": datetime.now(),
            "bets_count": len(self.bets)
        })

        # Ограничиваем историю
        if len(self.game_history) > 50:
            self.game_history = self.game_history[-50:]

    def generate_multiplier(self) -> float:
        """Генерация случайного множителя с математическим распределением"""
        # Формула для краш-игры: чем выше множитель, тем меньше вероятность
        r = random.random()
        if r < 0.1:  # 10% chance for 2x or less
            return round(random.uniform(1.1, 2.0), 2)
        elif r < 0.3:  # 20% chance for 2x-5x
            return round(random.uniform(2.0, 5.0), 2)
        elif r < 0.6:  # 30% chance for 5x-10x
            return round(random.uniform(5.0, 10.0), 2)
        else:  # 40% chance for 10x+
            return round(random.uniform(10.0, 100.0), 2)

    async def place_bet(self, user_id: int, amount: float, auto_cashout: float = None):
        """Размещение ставки"""
        if not self.is_playing:
            raise Exception("Game is not active")
            
        self.bets[user_id] = {
            "amount": amount,
            "auto_cashout": auto_cashout,
            "placed_at": datetime.now(),
            "cashed_out": False,
            "profit": 0
        }

    async def cash_out(self, user_id: int):
        """Вывод средств"""
        if user_id not in self.bets:
            raise Exception("No bet found")
            
        bet = self.bets[user_id]
        if bet["cashed_out"]:
            raise Exception("Already cashed out")
            
        profit = bet["amount"] * self.current_multiplier
        bet["cashed_out"] = True
        bet["profit"] = profit
        
        return profit