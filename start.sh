#!/bin/bash


# Запускаем бота
uvicorn app.main:app --host 0.0.0.0 --port $PORT