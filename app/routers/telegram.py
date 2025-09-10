from aiogram import Router, types
from aiogram.filters import CommandStart
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.crud import get_user_by_telegram_id as get_user, create_user  
from app.bot.bot import webapp_builder
from aiogram.types import Message
from app.database import crud

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.crud import update_user_language 

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.database.crud import get_user_by_telegram_id as get_user, create_user, update_user_language  
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
    # ✅ Извлекаем параметры из команды /start
    args = message.text.split()
    referrer_id = None
    
    # Ищем реферальный параметр (формат: /start ref_11)
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referrer_id = int(args[1].split('_')[1])
            print(f"🎯 Обнаружен реферальный код: {referrer_id}")
        except (IndexError, ValueError):
            print("❌ Неверный формат реферального кода")
    
    # Получаем или создаем пользователя с данными из Telegram
    user = get_user(db, message.from_user.id)
    if not user:
        user = create_user(
            db=db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,  # ✅ Сохраняем имя
            last_name=message.from_user.last_name     # ✅ Сохраняем фамилию
        )
        
        # ✅ Если это новый пользователь и есть реферальный код
        if referrer_id:
            from app.bot.bot import process_referral
            await process_referral(message.from_user.id, referrer_id, db)
    
    # ✅ Проверяем, есть ли уже выбранный язык
    if user.language:
        # Используем сохраненный язык
        lang = user.language
        greeting = generate_greeting(user, lang)
        
        await message.answer(greeting)
        await message.answer(
            get_continue_message(lang),
            reply_markup=webapp_builder()
        )
    else:
        # Язык не выбран, показываем выбор языка
        await message.answer("Выберите язык / Choose language / 选择语言:",
                           reply_markup=get_language_inline_keyboard())
        
    if user:
        update_fields = False
    
    if message.from_user.username != user.username:
        user.username = message.from_user.username
        update_fields = True
        
    if message.from_user.first_name != user.first_name:
        user.first_name = message.from_user.first_name
        update_fields = True
        
    if message.from_user.last_name != user.last_name:
        user.last_name = message.from_user.last_name
        update_fields = True
        
    if update_fields:
        db.commit()
        print(f"✅ Обновлены данные пользователя {user.id}")

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
        
        
def generate_greeting(user, lang: str) -> str:
    """Генерируем приветствие с учетом имени пользователя"""
    name_parts = []
    
    if user.first_name:
        name_parts.append(user.first_name)
    if user.last_name:
        name_parts.append(user.last_name)
    
    if name_parts:
        # Есть имя и/или фамилия
        full_name = " ".join(name_parts)
        greetings = {
            'ru': f"С возвращением, {full_name}! 👋",
            'en': f"Welcome back, {full_name}! 👋",
            'zh': f"欢迎回来, {full_name}! 👋"
        }
    else:
        # Используем username или общее обращение
        username = user.username or {
            'ru': 'друг',
            'en': 'friend', 
            'zh': '朋友'
        }[lang]
        
        greetings = {
            'ru': f"С возвращением, {username}! 👋",
            'en': f"Welcome back, {username}! 👋",
            'zh': f"欢迎回来, {username}! 👋"
        }
    
    return greetings[lang]

def get_continue_message(lang: str) -> str:
    """Получаем сообщение о продолжении на нужном языке"""
    messages = {
        'ru': "Рады снова вас видеть! Чем займемся сегодня? 🎮",
        'en': "Glad to see you again! What shall we do today? 🎮",
        'zh': "很高兴再次见到你！今天我们要做什么？🎮"
    }
    return messages[lang]

from aiogram.types import LabeledPrice, PreCheckoutQuery

async def stars_payment_handler(message: Message):
    """Обработчик команды покупки Stars"""
    prices = [LabeledPrice(label="STARS", amount=1000)]  # 10.00 STARS
    
    await message.answer_invoice(
        title="Пополнение STARS",
        description="Пополнение баланса STARS для игр",
        provider_token="",  # Для Stars оставляем пустым
        currency="XTR",     # Валюта Stars
        prices=prices,
        payload="stars_deposit",
        start_parameter="stars_payment"
    )

async def stars_pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Предварительная проверка платежа"""
    await pre_checkout_query.answer(ok=True)

async def stars_successful_payment_handler(message: Message):
    """Обработка успешного платежа"""
    payment_info = message.successful_payment
    await message.answer(f"✅ Успешно пополнено {payment_info.total_amount / 100} STARS!")