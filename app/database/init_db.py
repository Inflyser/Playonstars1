import os
from app.database.session import SessionLocal
from app.database import crud

async def init_test_data():
    """Инициализация тестовых данных"""
    if os.getenv('ENVIRONMENT') == 'development':
        db = SessionLocal()
        try:
            # Создаем тестового пользователя
            test_user = crud.create_user(
                db,
                telegram_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            
            # Создаем кошелек
            crud.create_wallet(
                db,
                test_user.id,
                "EQtest_wallet_address_123456789",
                "tonkeeper"
            )
            
            # Начальный баланс
            crud.update_user_balance(db, 123456789, "ton", 5.0)
            crud.update_user_balance(db, 123456789, "stars", 100.0)
            
            print("✅ Test data initialized")
            
        except Exception as e:
            print(f"❌ Error initializing test data: {e}")
        finally:
            db.close()