import asyncio
import random
from datetime import datetime

class CrashGame:
    def __init__(self, websocket_manager):
        self.ws_manager = websocket_manager  # ✅ Сохраняем менеджер
        self.current_multiplier = 1.0
        self.is_playing = False
        self.bets = {}
        self.game_history = []
        self.game_id = 0

    async def run_game_cycle(self):
        """Запуск цикла игры"""
        self.game_id += 1
        self.is_playing = True
        self.bets.clear()
        
        # Фаза приема ставок (15 секунд)
        await self.ws_manager.send_crash_update({  # ✅ Используем self.ws_manager
            "game_id": self.game_id,
            "phase": "betting",
            "time_remaining": 15,
            "multiplier": 1.0
        })
        
        for i in range(15, 0, -1):
            await asyncio.sleep(1)
            if not self.is_playing:
                return
                
            await self.ws_manager.send_crash_update({  # ✅ Используем self.ws_manager
                "game_id": self.game_id,
                "phase": "betting",
                "time_remaining": i,
                "multiplier": 1.0
            })

        # Генерируем множитель
        multiplier = self.generate_multiplier()
        
        # Фаза полета
        current_multiplier = 1.0
        step = 0.01
        
        while current_multiplier < multiplier and self.is_playing:
            await asyncio.sleep(0.1)
            current_multiplier += step
            current_multiplier = round(current_multiplier, 2)
            
            # Увеличиваем шаг для более динамичной игры
            if current_multiplier > 5:
                step = 0.05
            elif current_multiplier > 2:
                step = 0.02
            
            await self.ws_manager.send_crash_update({  # ✅ Используем self.ws_manager
                "game_id": self.game_id,
                "phase": "flying",
                "multiplier": current_multiplier,
                "time_remaining": 0
            })

        # Крах - игра окончена
        self.is_playing = False
        await self.ws_manager.send_crash_result({  # ✅ Используем self.ws_manager
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
        """Генерация случайного множителя"""
        return round(random.uniform(1.1, 10.0), 2)