from aiogram import Router, types
from aiogram.filters import CommandStart
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.crud import get_user, create_user
from app.bot.bot import webapp_builder
from aiogram.types import Message
from app.database import crud

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.crud import update_user_language 

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.database.crud import get_user, create_user, update_user_language
from aiogram.exceptions import TelegramBadRequest

router = Router()

# Создаем клавиатуру с инлайн-кнопками для трех языков
def get_language_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ],
            [
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh")
            ]
        ]
    )

@router.message(CommandStart())
async def cmd_start(message: Message, db: Session):
    # Получаем или создаем пользователя
    user = get_user(db, message.from_user.id)
    if not user:
        user = create_user(db, message.from_user.id, message.from_user.username)
    
    # Приветствие на текущем языке пользователя (или русском по умолчанию)
    lang = user.language if user and user.language else 'ru'
    greeting = {
        'ru': f"Привет, {user.username or 'друг'}! 👋",
        'en': f"Hello, {user.username or 'friend'}! 👋",
        'zh': f"你好, {user.username or '朋友'}! 👋"
    }[lang]
    
    await message.answer(greeting)
    await message.answer(
        "Выберите язык / Choose language / 选择语言:",
        reply_markup=get_language_inline_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith('lang_'))
async def process_language_callback(callback: CallbackQuery, db: Session):
    lang = callback.data.split('_')[1]  # 'ru', 'en' или 'zh'
    user = update_user_language(db, callback.from_user.id, lang)
    
    response = {
        'ru': 'Язык изменен на Русский ✅',
        'en': 'Language changed to English ✅',
        'zh': '语言已更改为中文 ✅'
    }[lang]
    
    duck_message = {
        'ru': 'Приложение работает!',
        'en': 'The application is working!',
        'zh': '應用程式正在運行！'
    }[lang]
    
    try:
        # 1. Отвечаем уведомлением
        await callback.answer(response)
        
        # 2. Удаляем кнопки из исходного сообщения
        await callback.message.edit_reply_markup(reply_markup=None)
        
        # 3. Отправляем новое сообщение с кнопкой WebApp
        await callback.message.answer(
            duck_message,
            reply_markup=webapp_builder()
        )
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            print("Message not modified, continuing...")
        else:
            print(f"Telegram API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await callback.answer("Произошла ошибка / An error occurred / 发生错误")