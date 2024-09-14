# handlers/payments.py

from aiogram import types
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import YKASSA_PROVIDER_TOKEN
from db.database import SessionLocal
from db.models import User, Payment
import logging
from datetime import datetime
from aiogram import Router
from aiogram.types import ContentType
from aiogram import F


router = Router()  # Инициализация router

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def process_pay_command(callback_query: types.CallbackQuery):
    """
    Обработчик команды для начала оплаты.
    Отправляет пользователю счет для оплаты подписки через ЮKassa.
    """
    prices = [LabeledPrice(label='Подписка на VPN', amount=50000)]  # Цена в копейках (500.00 руб)

    # Генерация кнопки для отмены платежа
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel_payment")
    cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

    await callback_query.message.bot.send_invoice(
        callback_query.from_user.id,
        title='Подписка на VPN',
        description='Оплатите подписку на VPN на 1 месяц',
        provider_token=YKASSA_PROVIDER_TOKEN,
        currency='RUB',
        prices=prices,
        payload='vpn_subscription_payload',
        need_email=True,  # Можно убрать, если не нужно
        need_phone_number=True,  # Можно убрать, если не нужно
        reply_markup=cancel_keyboard  # Клавиатура с кнопкой отмены
    )


@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """
    Обработчик PreCheckoutQuery перед подтверждением платежа.
    """
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def handle_successful_payment(message: types.Message):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        payment = Payment(
            user_id=user.id,
            telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
            provider_payment_charge_id=message.successful_payment.provider_payment_charge_id,
            amount=message.successful_payment.total_amount / 100,  # Конвертация копеек в рубли
            currency=message.successful_payment.currency,
            description='Подписка на VPN',
            created_at=datetime.utcnow(),
            status='completed'
        )
        db.add(payment)
        db.commit()
        await message.answer('Спасибо за оплату! Ваша подписка активирована.')
    except Exception as e:
        logging.error(f"Ошибка при сохранении платежа: {e}")
        await message.answer('Произошла ошибка при обработке вашего платежа. Пожалуйста, свяжитесь с поддержкой.')
    finally:
        db.close()

