import asyncio
import random
import math
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud
from app.database.models import User

class CrashGame:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.current_multiplier = 1.0
        self.is_playing = False
        self.bets = {}  # user_id -> bet_data
        self.game_history = []
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
            "time_remaining": 15,
            "multiplier": 1.0
        })
        
        for i in range(15, 0, -1):
            await asyncio.sleep(1)
            if not self.is_playing:
                return
                
            await self.ws_manager.send_crash_update({
                "game_id": self.game_id,
                "phase": "betting",
                "time_remaining": i,
                "multiplier": 1.0
            })

        # Генерируем множитель с RTP 95%
        multiplier = self.generate_multiplier_rtp_95()
        
        # Фаза полета
        current_multiplier = 1.0
        step = 0.01
        
        while current_multiplier < multiplier and self.is_playing:
            await asyncio.sleep(0.1)
            current_multiplier += step
            current_multiplier = round(current_multiplier, 2)
            
            if current_multiplier > 5:
                step = 0.05
            elif current_multiplier > 2:
                step = 0.02
            
            await self.ws_manager.send_crash_update({
                "game_id": self.game_id,
                "phase": "flying",
                "multiplier": current_multiplier,
                "time_remaining": 0
            })

        # Крах - игра окончена
        self.is_playing = False
        
        # ✅ СОХРАНЯЕМ РЕЗУЛЬТАТЫ В БД
        await self.save_game_results(multiplier)
        
        await self.ws_manager.send_crash_result({
            "game_id": self.game_id,
            "final_multiplier": multiplier,
            "crashed_at": multiplier,
            "timestamp": datetime.now().isoformat()
        })

    def generate_multiplier_rtp_95(self) -> float:
        """
        Генерация множителя с RTP 95%
        
        Формула: P(x) = (1 - RTP) / x^2
        Где RTP = 0.95, поэтому P(x) = 0.05 / x^2
        
        Интеграл от 1 до ∞: ∫(0.05/x^2)dx = 0.05
        
        Метод обратного преобразования:
        u = ∫(1/x^2)dx от 1 до x = 1 - 1/x
        x = 1/(1 - u)
        """
        u = random.random()
        
        # 5% вероятность краха на 1x (RTP 95%)
        if u < 0.05:
            return 1.0
        
        # Генерируем множитель по формуле x = 1/(1 - u)
        # Но нам нужно учесть, что u уже > 0.05, поэтому масштабируем
        scaled_u = 0.05 + u * 0.95  # Масштабируем до [0.05, 1.0]
        multiplier = 1.0 / (1.0 - scaled_u)
        
        # Ограничиваем максимальный множитель (например, 1000x)
        multiplier = min(multiplier, 1000.0)
        
        # Округляем до 2 знаков после запятой
        return round(multiplier, 2)

    # Альтернативная реализация с экспоненциальным распределением
    def generate_multiplier_exponential(self) -> float:
        """
        Альтернативная реализация с экспоненциальным распределением
        для достижения RTP 95%
        """
        # Параметр для экспоненциального распределения
        # E[x] = 1/λ = 20, поэтому λ = 0.05
        lambda_param = 0.05
        
        # Генерируем случайную величину
        u = random.random()
        multiplier = -math.log(1 - u) / lambda_param
        
        # Ограничиваем минимальный множитель 1.0
        multiplier = max(multiplier, 1.0)
        
        # Ограничиваем максимальный множитель
        multiplier = min(multiplier, 1000.0)
        
        return round(multiplier, 2)

    # Оригинальный метод (оставлен для совместимости)
    def generate_multiplier(self) -> float:
        """Генерация случайного множителя (оригинальная версия)"""
        return round(random.uniform(1.1, 10.0), 2)



    async def save_game_results(self, final_multiplier: float):
        """Сохраняем результаты игры в базу данных"""
        db = SessionLocal()
        try:
            total_players = len(self.bets)
            total_bet = sum(bet['amount'] for bet in self.bets.values())
            total_payout = 0.0
            
            # Сохраняем результат игры
            game_result = crud.create_crash_game_result(
                db=db,
                game_id=self.game_id,
                multiplier=final_multiplier,
                crashed_at=final_multiplier,
                total_players=total_players,
                total_bet=total_bet,
                total_payout=total_payout
            )
            
            db.commit()
            db.refresh(game_result)
            
            # Обрабатываем каждую ставку
            for user_id, bet_data in self.bets.items():
                # ✅ Используем get_user_by_id которую сейчас добавим в crud.py
                user = crud.get_user_by_id(db, user_id)
                if not user:
                    print(f"❌ User {user_id} not found in DB")
                    continue
                
                # ✅ Используем bet_id который сохранили при размещении ставки
                if 'bet_id' in bet_data:
                    # Определяем результат ставки
                    if bet_data.get('cashed_out', False):
                        cashout_multiplier = bet_data.get('cashout_multiplier', 1.0)
                        win_amount = bet_data['amount'] * cashout_multiplier
                        status = 'won'
                    elif final_multiplier >= (bet_data.get('auto_cashout', 0) or 0):
                        win_amount = bet_data['amount'] * bet_data['auto_cashout']
                        status = 'won'
                    else:
                        win_amount = 0
                        status = 'lost'
                    
                    # Обновляем ставку в БД
                    crud.update_crash_bet_result(
                        db=db,
                        bet_id=bet_data['bet_id'],
                        crash_coefficient=final_multiplier,
                        win_amount=win_amount,
                        status=status
                    )
                    
                    # Обновляем баланс пользователя если выигрыш
                    if win_amount > 0:
                        crud.update_user_balance(
                            db=db,
                            telegram_id=user.telegram_id,
                            currency='stars',
                            amount=win_amount
                        )
                    
                    total_payout += win_amount
            
            # Обновляем общий выигрыш в результате игры
            game_result.total_payout = total_payout
            db.commit()
            
            print(f"✅ Результаты игры сохранены: Game ID {self.game_id}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения результатов игры: {e}")
            db.rollback()
        finally:
            db.close()

    def generate_multiplier(self) -> float:
        """Генерация случайного множителя"""
        return round(random.uniform(1.1, 10.0), 2)

    async def place_bet(self, user_id: int, amount: float, auto_cashout: float = None):
        """Размещение ставки с сохранением в БД"""
        print(f"🎯 [CrashGame] place_bet called: user_id={user_id}, amount={amount}")

        db = SessionLocal()
        try:
            # ✅ Важно: user_id должен быть ID из БД, а не telegram_id!
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"❌ [CrashGame] User {user_id} not found by ID")
                return False

            print(f"✅ [CrashGame] User found: ID {user.id}, Telegram ID {user.telegram_id}")

            # Создаем запись о ставке в БД
            bet = crud.add_crash_bet(
                db=db,
                user_id=user.id,  # ✅ ID из БД
                telegram_id=user.telegram_id,  # ✅ Telegram ID
                bet_amount=amount,
                status='pending'
            )

            # Сохраняем в активные ставки
            self.bets[user.id] = {
                "amount": amount,
                "auto_cashout": auto_cashout,
                "placed_at": datetime.now(),
                "cashed_out": False,
                "profit": 0,
                "bet_id": bet.id  # ✅ Сохраняем ID ставки
            }

            print(f"✅ [CrashGame] Bet added to active bets: {bet.id}")
            return True

        except Exception as e:
            print(f"❌ [CrashGame] Error in place_bet: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False
        finally:
            db.close()

    async def cash_out(self, user_id: int, cashout_multiplier: float):
        """Вывод средств с обновлением в БД"""
        if user_id not in self.bets:
            raise Exception("No active bet found")
        
        bet_data = self.bets[user_id]
        bet_data['cashed_out'] = True
        bet_data['cashout_multiplier'] = cashout_multiplier
        bet_data['profit'] = bet_data['amount'] * cashout_multiplier