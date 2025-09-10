import math
import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database import crud
from app.database.models import User
import asyncio



class CrashGame:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.current_multiplier = 1.0
        self.is_playing = False
        self.bets = {}
        self.game_history = []
        self.game_id = 0
        self.settings = None

    def load_settings(self, db: Session):
        """Загружаем настройки из БД"""
        from app.database import crud
        self.settings = crud.get_game_settings(db)
        return self.settings

    def generate_multiplier(self) -> float:
        """Простая генерация множителя"""
        db = SessionLocal()
        try:
            settings = crud.get_game_settings(db)
            if not settings:
                return round(random.uniform(1.1, 10.0), 2)

            # ✅ ПРОСТАЯ ФОРМУЛА - без сложных распределений
            base = random.uniform(1.1, 5.0)
            multiplier = base * (1 + (1 - settings.crash_rtp))

            # Ограничиваем мин/макс
            multiplier = max(settings.crash_min_multiplier, 
                            min(settings.crash_max_multiplier, multiplier))

            return round(multiplier, 2)

        finally:
            db.close()
            
    async def run_game_cycle(self):
        """Запуск цикла игры с учетом настроек"""
        # Загружаем актуальные настройки
        db = SessionLocal()
        self.load_settings(db)
        db.close()
        
        self.game_id += 1
        self.is_playing = True
        self.bets.clear()
        
        # Фаза приема ставок
        await self.ws_manager.send_crash_update({
            "game_id": self.game_id,
            "phase": "betting",
            "time_remaining": 15,
            "multiplier": 1.0,
            "settings": {
                "rtp": self.settings.crash_rtp if self.settings else 0.95,
                "min_multiplier": self.settings.min_multiplier if self.settings else 1.1,
                "max_multiplier": self.settings.max_multiplier if self.settings else 100.0
            }
        })
        
        # Ожидание приема ставок (15 секунд)
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

        # Генерируем множитель
        multiplier = self.generate_multiplier()
        
        # Фаза полета
        current_multiplier = 1.0
        step = 0.01
        
        while current_multiplier < multiplier and self.is_playing:
            await asyncio.sleep(0.1)
            current_multiplier += step
            current_multiplier = round(current_multiplier, 2)
            
            # Увеличиваем шаг для больших множителей
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
        
        # Сохраняем результаты
        await self.save_game_results(multiplier)
        
        await self.ws_manager.send_crash_result({
            "game_id": self.game_id,
            "final_multiplier": multiplier,
            "crashed_at": multiplier,
            "timestamp": datetime.now().isoformat()
        })

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
                user = crud.get_user_by_id(db, user_id)
                if not user:
                    print(f"❌ User {user_id} not found in DB")
                    continue
                
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

    async def place_bet(self, user_id: int, amount: float, auto_cashout: float = None):
        """Размещение ставки с сохранением в БД"""
        print(f"🎯 [CrashGame] place_bet called: user_id={user_id}, amount={amount}")

        db = SessionLocal()
        try:
            # Получаем пользователя по ID
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"❌ [CrashGame] User {user_id} not found by ID")
                return False

            # Проверяем достаточно ли средств
            if user.stars_balance < amount:
                print(f"❌ [CrashGame] Insufficient balance: {user.stars_balance} < {amount}")
                return False

            # Создаем запись о ставке в БД
            bet = crud.add_crash_bet(
                db=db,
                user_id=user.id,
                telegram_id=user.telegram_id,
                bet_amount=amount,
                status='pending'
            )

            # Списываем средства с баланса
            crud.update_user_balance(
                db=db,
                telegram_id=user.telegram_id,
                currency='stars',
                amount=-amount
            )

            # Сохраняем в активные ставки
            self.bets[user.id] = {
                "amount": amount,
                "auto_cashout": auto_cashout,
                "placed_at": datetime.now(),
                "cashed_out": False,
                "profit": 0,
                "bet_id": bet.id
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
        
        # Немедленно обновляем баланс пользователя
        db = SessionLocal()
        try:
            user = crud.get_user_by_id(db, user_id)
            if user:
                win_amount = bet_data['amount'] * cashout_multiplier
                crud.update_user_balance(
                    db=db,
                    telegram_id=user.telegram_id,
                    currency='stars',
                    amount=win_amount
                )
                db.commit()
        except Exception as e:
            print(f"❌ Error in cash_out: {e}")
            db.rollback()
        finally:
            db.close()