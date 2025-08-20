#!/bin/bash
# Применяем миграции перед запуском
# alembic upgrade head || echo "Миграции не применились, продолжаем запуск..."

# Запускаем бота
uvicorn app.main:app --host 0.0.0.0 --port $PORT