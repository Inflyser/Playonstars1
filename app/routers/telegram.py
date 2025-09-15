from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from fastapi import Depends
from sqlalchemy.orm import Session
from aiogram import Router, F, Bot
from app.database.session import get_db
from app.database.crud import get_user_by_telegram_id as get_user, create_user  
from app.bot.bot import webapp_builder
from aiogram.types import Message, Optional
from app.database import crud
from aiogram.utils.deep_linking import decode_payload
from app.database.models import User, ReferralAction

import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.database.crud import update_user_language, get_user_by_telegram_id

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.database.crud import get_user_by_telegram_id as get_user, create_user, update_user_language  
from aiogram.exceptions import TelegramBadRequest
from app.services import stars_service
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
async def cmd_start_regular(message: Message, db: Session):
    """Обработчик для обычного /start БЕЗ параметров"""
    print("ℹ️ REGULAR: Обычный /start без параметров")
    
    # Логика для обычного старта
    user = get_user_by_telegram_id(db, message.from_user.id)
    if not user:
        user = create_user(
            db=db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        print(f"✅ Создан новый пользователь. ID: {user.id}")
    
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

@router.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(message: Message, command: CommandObject, db: Session):
    """Единственный обработчик для /start с реферальными ссылками"""
    try:
        args = command.args
        print(f"🎯 DEEP_LINK: Получены аргументы: '{args}'")
        
        # 1. Извлекаем telegram_id реферера из ссылки
        referrer_telegram_id = None
        if args and args.startswith('ref_'):
            try:
                referrer_telegram_id = int(args.split('_')[1])
                print(f"✅ Извлечен реферальный telegram_id: {referrer_telegram_id}")
            except (IndexError, ValueError) as e:
                print(f"❌ Ошибка извлечения telegram_id: {e}")
                referrer_telegram_id = None
        else:
            print("ℹ️ Аргументы не содержат реферальной ссылки")
            return

        # 2. Ищем текущего пользователя в БД
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            # 3. СОЗДАЕМ НОВОГО ПОЛЬЗОВАТЕЛЯ
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name, 
                last_name=message.from_user.last_name
            )
            db.add(user)
            db.flush()  # Сохраняем, чтобы получить ID
            print(f"✅ Создан новый пользователь. ID: {user.id}, telegram_id: {user.telegram_id}")

            # 4. ОБРАБАТЫВАЕМ РЕФЕРАЛА
            if referrer_telegram_id:
                print(f"🔍 Ищем реферера в БД по telegram_id: {referrer_telegram_id}")
                referrer = db.query(User).filter(User.telegram_id == referrer_telegram_id).first()
                
                if referrer:
                    print(f"✅ Найден реферер. ID: {referrer.id}, telegram_id: {referrer.telegram_id}")
                    
                    # 5. ОБНОВЛЯЕМ СТАТИСТИКУ РЕФЕРЕРА
                    referrer.referrals_count = (referrer.referrals_count or 0) + 1
                    referrer.active_referrals = (referrer.active_referrals or 0) + 1
                    
                    # 6. УСТАНАВЛИВАЕМ СВЯЗЬ
                    user.referrer_id = referrer.id
                    
                    # 7. СОЗДАЕМ ЗАПИСЬ В HISTORy
                    referral_action = ReferralAction(
                        referrer_id=referrer.id,
                        referral_id=user.id,
                        action_type='registration',
                        action_amount=0.0,
                        reward_amount=0.0
                    )
                    db.add(referral_action)
                    
                    print(f"✅ Реферальная связь установлена: {user.id} -> {referrer.id}")
                    print(f"📊 Обновлены счетчики: referrals_count={referrer.referrals_count}, active_referrals={referrer.active_referrals}")
                else:
                    print(f"⚠️ Реферер с telegram_id {referrer_telegram_id} не найден в БД")
        
        # 8. КОММИТИМ ВСЕ ИЗМЕНЕНИЯ
        db.commit()
        print(f"💾 Все изменения успешно сохранены в БД")
        
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
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в обработчике: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    
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
    
    
from aiogram.types import LabeledPrice
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)

@router.message(Command("buy_stars"))
async def cmd_buy_stars(message: Message, db: Session = Depends(get_db)):
    """Команда для покупки Stars - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        user = crud.get_user(db, message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return

        # Указываем количество Stars (например, 100)
        stars_amount = 5
        
        # ⚠️ ВАЖНО: для Stars amount указывается как есть, без умножения на 100!
        prices = [LabeledPrice(label="XTR", amount=stars_amount)]

        await message.answer_invoice(
            title="Пополнение STARS",
            description=f"Пополнение баланса на {stars_amount} STARS",
            currency="XTR",
            prices=prices,
            provider_token="",  # ⚠️ ОБЯЗАТЕЛЬНО пустая строка для Stars!
            payload=f"stars:{message.from_user.id}:{stars_amount}",  # Простая строка
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
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Всегда подтверждаем pre-checkout для Stars"""
    try:
        logger.info(f"Pre-checkout received: {pre_checkout_query}")
        await pre_checkout_query.answer(ok=True)
        logger.info("Pre-checkout approved")
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment error")

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, db: Session = Depends(get_db)):
    """Обработка успешного платежа Stars"""
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        logger.info(f"✅ Successful payment received: {payment}")
        
        # Парсим payload (формат: "stars:user_id:amount")
        payload_parts = payment.invoice_payload.split(':')
        if len(payload_parts) != 3 or payload_parts[0] != 'stars':
            raise ValueError("Invalid payload format")
            
        target_user_id = int(payload_parts[1])
        stars_amount = int(payload_parts[2])
        
        # Проверяем пользователя
        if user_id != target_user_id:
            logger.error(f"User ID mismatch: {user_id} != {target_user_id}")
            await message.answer("❌ Security error")
            return
        
        user = crud.get_user(db, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            await message.answer("❌ User not found")
            return
        
        # Зачисляем средства
        user.stars_balance += stars_amount
        db.commit()
        
        logger.info(f"💰 Added {stars_amount} STARS to user {user_id}. New balance: {user.stars_balance}")
        
        await message.answer(
            f"✅ Payment successful!\n"
            f"💫 Added: {stars_amount} STARS\n"
            f"💰 New balance: {user.stars_balance} STARS\n\n"
            f"Thank you for your purchase! 🎮"
        )
        
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        await message.answer("❌ Payment processing error")

from aiogram.types import PreCheckoutQuery, SuccessfulPayment
from aiogram.filters import Command

# ✅ ОБЯЗАТЕЛЬНЫЙ обработчик для предварительной проверки
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """ВСЕГДА подтверждаем pre-checkout для Stars"""
    try:
        logger.info(f"Pre-checkout received: {pre_checkout_query}")
        await pre_checkout_query.answer(ok=True)
        logger.info("Pre-checkout approved")
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment error")

# ✅ Обработчик успешных платежей
@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message, db: Session = Depends(get_db)):
    """Обработка успешного платежа"""
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        logger.info(f"✅ Successful payment received: {payment}")
        
        # Парсим payload
        payload_parts = payment.invoice_payload.split(':')
        if len(payload_parts) != 3 or payload_parts[0] != 'stars':
            await message.answer("❌ Invalid payment payload")
            return
            
        target_user_id = int(payload_parts[1])
        stars_amount = int(payload_parts[2])
        
        # Проверяем пользователя
        if user_id != target_user_id:
            await message.answer("❌ Security error")
            return
        
        user = get_user(db, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        # Зачисляем средства
        user.stars_balance += stars_amount
        db.commit()
        
        await message.answer(
            f"✅ Payment successful!\n"
            f"💫 Added: {stars_amount} Stars\n"
            f"💰 New balance: {user.stars_balance} Stars"
        )
        
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await message.answer("❌ Payment processing error")

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
   
   

        
@router.message(Command("test_payment"))
async def cmd_test_payment(message: Message):
    """Тестовая команда для проверки платежа"""
    try:
        # Тестовая сумма - 10 STARS
        invoice_link = await stars_service.create_invoice(message.from_user.id, 10)
        
        if invoice_link:
            await message.answer(
                f"🧪 Test payment - 10 STARS\n\n"
                f"Click to pay: {invoice_link}\n\n"
                f"💡 This is a test payment to verify the system works correctly.",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Failed to create test invoice")
            
    except Exception as e:
        logger.error(f"Test payment error: {e}")
        await message.answer("❌ Test payment error")
        
        

@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Session = Depends(get_db)):
    """ЕДИНСТВЕННЫЙ обработчик команды /admin"""
    text = message.text.strip()
    
    # Если просто /admin - проверяем статус
    if len(text.split()) == 1:
        is_admin = crud.is_user_admin(db, message.from_user.id)
        if is_admin:
            await message.answer("✅ Вы уже являетесь администратором!")
        else:
            await message.answer("❌ Вы не администратор. Для получения прав используйте: /admin секретный_код")
        return
    
    # Проверяем секретный код
    secret_code = text.split(" ", 1)[1].strip()
    
    # Твой секретный код для добавления админов
    if secret_code == "KBV4B92clwn8juHJHF45106KBNJHF31cvo2pl5g":
        # Добавляем пользователя в админы
        admin = crud.add_admin_user(
            db, 
            message.from_user.id, 
            message.from_user.username
        )
        
        await message.answer(
            f"✅ Вы стали администратором!\n\n"
            f"Теперь вы можете:\n"
            f"• Открыть приложение\n"
            f"• Видеть кнопку \"⚙️ Админка\"\n"
            f"• Управлять настройками\n\n"
            f"Ваш Telegram ID: {message.from_user.id}",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Неверный секретный код")