from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.crud import get_user_by_telegram_id as get_user, create_user  
from app.bot.bot import webapp_builder
from aiogram.types import Message
from app.database import crud
from aiogram.utils.deep_linking import decode_payload

import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.crud import update_user_language, get_user_by_telegram_id

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
async def cmd_start(message: Message, command: CommandObject = None, db: Session = Depends(get_db)):
    # Извлекаем аргументы из команды /start
    args = command.args if command and command.args else message.text.split()[1] if len(message.text.split()) > 1 else None
    
    referrer_telegram_id = None
    print(f"🎯 Получена команда /start с аргументами: {args}")

    # 1. Извлекаем telegram_id из ссылки
    if args and args.startswith('ref_'):
        try:
            referrer_telegram_id = int(args.split('_')[1])
            print(f"✅ Извлечен реферальный telegram_id: {referrer_telegram_id}")
        except (IndexError, ValueError) as e:
            print(f"❌ Ошибка извлечения telegram_id из ссылки: {e}")
            referrer_telegram_id = None

    user = get_user_by_telegram_id(db, message.from_user.id)
    if not user:
        # Создаем нового пользователя
        user = create_user(
            db=db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        print(f"✅ Создан новый пользователь. Его ID в БД: {user.id}, telegram_id: {user.telegram_id}")

        # 2. ОБРАБОТКА РЕФЕРАЛА: Если есть реферальная ссылка
        if referrer_telegram_id:
            print(f"🔍 Поиск реферера в БД по telegram_id: {referrer_telegram_id}")
            # НАХОДИМ реферера в БД по его telegram_id
            referrer_user = get_user_by_telegram_id(db, referrer_telegram_id)
            if referrer_user:
                print(f"✅ Найден реферер. Его ID в БД: {referrer_user.id}, telegram_id: {referrer_user.telegram_id}")
                # ПЕРЕДАЕМ ВНУТРЕННИЕ ID В БАЗЕ ДАННЫХ
                from app.bot.bot import process_referral
                success = await process_referral(new_user_id=user.id, referrer_id=referrer_user.id, db=db)
                if success:
                    print(f"✅ Реферальная связь установлена: новый пользователь (id={user.id}) -> реферер (id={referrer_user.id})")
                else:
                    print(f"❌ Не удалось обработать реферала для пользователя с id={user.id}")
            else:
                print(f"⚠️ В БД не найден пользователь с telegram_id={referrer_telegram_id}. Реферальная ссылка не обработана.")
    else:
        print(f"ℹ️ Пользователь с telegram_id={message.from_user.id} уже существует в БД (id={user.id}). Реферальная ссылка не обрабатывается.")
    
    # Обновляем данные пользователя если нужно
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

    # Логика с языком
    if user.language:
        lang = user.language
        greeting = generate_greeting(user, lang)
        
        await message.answer(greeting)
        await message.answer(
            get_continue_message(lang),
            reply_markup=webapp_builder()
        )
    else:
        await message.answer("Выберите язык / Choose language / 选择语言:",
                           reply_markup=get_language_inline_keyboard())

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
    prices = [LabeledPrice(label="STARS", amount=10)]  # 10.00 STARS
    
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
    await message.answer(f"✅ Успешно пополнено {payment_info.total_amount} STARS!")
    
    
from aiogram.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from aiogram.filters import Command
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@router.message(Command("buy_stars"))
async def cmd_buy_stars(message: Message, db: Session = Depends(get_db)):
    """Команда для покупки Stars"""
    try:
        user = get_user(db, message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return

        # ✅ ПРАВИЛЬНЫЙ формат цен для Stars
        stars_amount = 100  # 100 STARS
        prices = [LabeledPrice(label=f"{stars_amount} STARS", amount=stars_amount)]
        
        await message.answer_invoice(
            title="Пополнение STARS",
            description=f"Пополнение баланса на {stars_amount} STARS",
            provider_token="",  # ✅ ДЛЯ STARS ОСТАВЛЯЕМ ПУСТЫМ
            currency="XTR",     # ✅ ВАЛЮТА TELEGRAM STARS
            prices=prices,
            payload=json.dumps({  # ✅ ПРОСТОЙ JSON
                "type": "stars_payment",
                "user_id": message.from_user.id,
                "amount": stars_amount
            }),
            start_parameter="stars_payment",
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False
        )
        
    except Exception as e:
        logger.error(f"Error creating stars invoice: {e}")
        await message.answer("❌ Ошибка при создании платежа")

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, db: Session = Depends(get_db)):
    """Обработка предварительной проверки платежа"""
    try:
        # ✅ ВСЕГДА ПОДТВЕРЖДАЕМ ДЛЯ STARS
        await pre_checkout_query.answer(ok=True)
        
        logger.info(f"Pre-checkout approved for {pre_checkout_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment error")

@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message, db: Session = Depends(get_db)):
    """Обработка УСПЕШНОГО платежа - ТОЛЬКО ЗДЕСЬ зачисляем средства!"""
    try:
        payment: SuccessfulPayment = message.successful_payment
        user_id = message.from_user.id
        
        logger.info(f"Successful payment: {payment.to_python()}")
        
        # ✅ Парсим payload для получения данных
        payload_parts = payment.invoice_payload.split(':')
        if len(payload_parts) != 3 or payload_parts[0] != 'stars_deposit':
            logger.error(f"Invalid payload format: {payment.invoice_payload}")
            await message.answer("❌ Ошибка обработки платежа")
            return
        
        target_user_id = int(payload_parts[1])
        stars_amount = int(payload_parts[2])
        
        # ✅ Проверяем что платеж именно в Stars
        if payment.currency != 'XTR':
            logger.error(f"Invalid currency: {payment.currency}")
            await message.answer("❌ Неверная валюта платежа")
            return
        
        # ✅ Проверяем что пользователь совпадает
        if user_id != target_user_id:
            logger.error(f"User mismatch: {user_id} != {target_user_id}")
            await message.answer("❌ Ошибка безопасности платежа")
            return
        
        # ✅ ПРОВЕРЯЕМ НЕ ОБРАБАТЫВАЛИ ЛИ УЖЕ ЭТОТ ПЛАТЕЖ
        payment_id = payment.telegram_payment_charge_id
        
        user = get_user(db, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Проверка на дубликат платежа
        if user.stars_payment_ids and payment_id in user.stars_payment_ids:
            logger.warning(f"Duplicate payment detected: {payment_id}")
            await message.answer("⚠️ Этот платеж уже был обработан ранее")
            return
        
        # ✅ ЗАЧИСЛЯЕМ СРЕДСТВА НА БАЛАНС
        user.stars_balance += stars_amount
        
        # ✅ СОХРАНЯЕМ ID ПЛАТЕЖА ДЛЯ ПРЕДОТВРАЩЕНИЯ ДУБЛИКАТОВ
        if user.stars_payment_ids is None:
            user.stars_payment_ids = []
        user.stars_payment_ids.append(payment_id)
        
        db.commit()
        
        logger.info(f"Added {stars_amount} STARS to user {user_id}. New balance: {user.stars_balance}")
        
        # ✅ ОТПРАВЛЯЕМ ПОДТВЕРЖДЕНИЕ ПОЛЬЗОВАТЕЛЮ
        await message.answer(
            f"✅ Успешно пополнено {stars_amount} STARS!\n"
            f"💫 Новый баланс: {user.stars_balance} STARS\n\n"
            f"Спасибо за покупку! 🎮"
        )
        
        # ✅ ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ Через WEBSOCKET (если пользователь в веб-апп)
        try:
            from app.services.websocket_manager import websocket_manager
            await websocket_manager.send_to_user(
                f"user_{user_id}",
                {
                    "type": "balance_update",
                    "currency": "stars",
                    "new_balance": user.stars_balance,
                    "amount_added": stars_amount
                }
            )
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        await message.answer("❌ Ошибка при обработке платежа")

# Добавляем команду для проверки баланса
@router.message(Command("balance"))
async def cmd_balance(message: Message, db: Session = Depends(get_db)):
    """Проверка баланса пользователя"""
    user = get_user(db, message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    await message.answer(
        f"💰 Ваш баланс:\n"
        f"⭐ STARS: {user.stars_balance}\n"
        f"💎 TON: {user.ton_balance}\n\n"
        f"Для пополнения STARS используйте /buy_stars"
    )
    
@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Session = Depends(get_db)):
    """Команда для доступа к админке"""
    text = message.text.strip()
    
    if len(text.split()) == 1:
        # Просто /admin - просим пароль
        await message.answer(
            "🔐 Введите пароль админа:\n"
            "Пример: /admin ваш_пароль"
        )
        return
    
    # Проверяем пароль
    password = text.split(" ", 1)[1]
    settings = crud.get_game_settings(db)
    
    if not settings or password != settings.admin_password:
        await message.answer("❌ Неверный пароль админа")
        return
    
    # Показываем текущие настройки
    await message.answer(
        f"⚙️ Текущие настройки:\n"
        f"• RTP: {settings.crash_rtp}\n"
        f"• Мин. множитель: {settings.crash_min_multiplier}\n"
        f"• Макс. множитель: {settings.crash_max_multiplier}\n\n"
        f"Для изменения используйте API запросы"
    )