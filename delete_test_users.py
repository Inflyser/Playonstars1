import psycopg2
import os

# Данные подключения из вашего .env
DB_URL = "postgresql://play_on_stars_user:eTM7z3gxGQqcst4N5YDjD0zyQLxuhoKZ@dpg-d2jii17diees73c9kn3g-a.frankfurt-postgres.render.com/play_on_stars"

def delete_test_users():
    try:
        # Подключаемся к базе
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Удаляем тестовых пользователей
        cur.execute("DELETE FROM users WHERE telegram_id IN (123456789, 999888777)")
        
        # Проверяем сколько строк было удалено
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"✅ Удалено {deleted_count} тестовых пользователей")
        
        # Закрываем соединение
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при удалении: {e}")

if __name__ == "__main__":
    delete_test_users()