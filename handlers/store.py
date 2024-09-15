# store.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.database import SessionLocal
from db.models import Router as RouterModel, User
from sqlalchemy import func
from datetime import datetime
import logging

router = Router()

@router.message(Command("store"))
async def show_store(message: types.Message):
    """Обработчик для отображения интернет-магазина."""
    logging.info("Хендлер show_store сработал")
    session = SessionLocal()
    try:
        # Группировка роутеров по SKU и получение их количества для доступных к продаже
        routers = session.query(
            RouterModel.sku,
            RouterModel.model,
            func.count(RouterModel.id).label('quantity')
        ).filter(
            RouterModel.status == "available",
            RouterModel.is_for_sale == True
        ).group_by(
            RouterModel.sku,
            RouterModel.model
        ).all()

        if not routers:
            await message.answer("В магазине пока нет доступных роутеров.")
            return

        # Создание списка доступных роутеров
        text = "📦 **Магазин роутеров**\n\n"
        for router_item in routers:
            text += f"**Модель**: {router_item.model}\n"
            text += f"**SKU**: {router_item.sku}\n"
            text += f"**Доступно**: {router_item.quantity} шт.\n\n"

        # Кнопка для оформления заказа
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оформить заказ", callback_data="place_order")]
        ])

        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Произошла ошибка при загрузке магазина: {e}")
        await message.answer("Произошла ошибка при загрузке магазина.")
    finally:
        session.close()

@router.callback_query(lambda c: c.data == "place_order")
async def place_order(callback_query: types.CallbackQuery):
    """Обработчик для оформления заказа."""
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        # Ищем пользователя
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            await callback_query.message.answer("Пользователь не найден. Пожалуйста, зарегистрируйтесь.")
            return

        # Находим первый доступный к продаже роутер
        router_item = session.query(RouterModel).filter(
            RouterModel.status == "available",
            RouterModel.is_for_sale == True
        ).first()
        if not router_item:
            await callback_query.message.answer("К сожалению, все роутеры проданы.")
            return

        # Привязываем роутер к пользователю и меняем его статус
        router_item.user_id = user.id
        router_item.status = "sold"
        router_item.sale_date = datetime.utcnow()
        session.commit()

        await callback_query.message.answer(
            f"Роутер {router_item.model} (SKU: {router_item.sku}) успешно продан и привязан к вашей учетной записи."
        )
    
    except Exception as e:
        logging.error(f"Произошла ошибка при оформлении заказа: {e}")
        await callback_query.message.answer("Произошла ошибка при оформлении заказа.")
    finally:
        session.close()
        await callback_query.answer()
