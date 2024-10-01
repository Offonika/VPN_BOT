# admin.py

from aiogram import Bot, types, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from db.database import SessionLocal
from db.models import Router
from utils.barcode_scanner import scan_label
from io import BytesIO
import logging
import secrets

class RouterRegistration(StatesGroup):
    waiting_for_serial_number = State()
    waiting_for_model = State()
    waiting_for_mac_address = State()
    waiting_for_sku = State()

async def cmd_register_router(message: types.Message):
    """Обработчик команды /register_router для начала процесса регистрации роутера."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вручную", callback_data="add_router_manually")],
        [InlineKeyboardButton(text="Сканировать", callback_data="scan_router_label")]
    ])
    await message.answer("Выберите способ добавления роутера:", reply_markup=keyboard)

async def handle_router_image(message: types.Message, bot: Bot):
    """Обработчик для загрузки изображения роутера."""
    if not message.photo:
        await message.answer("Пожалуйста, отправьте корректное изображение.")
        return

    photo = message.photo[-1]
    file = await bot.download_file_by_id(photo.file_id)
    file_data = BytesIO(await file.read())

    result = await scan_label(file_data)

    if result:
        serial_number = result.get('serial_number')
        model = result.get('model')

        session = SessionLocal()
        try:
            new_router = Router(serial_number=serial_number, model=model)
            session.add(new_router)
            session.commit()
            await message.answer(f"Роутер {model} с серийным номером {serial_number} успешно зарегистрирован.")
        except Exception as e:
            logging.error(f"Ошибка при регистрации роутера: {e}")
            await message.answer("Произошла ошибка при регистрации роутера.")
        finally:
            session.close()
    else:
        await message.answer("Не удалось распознать данные. Пожалуйста, попробуйте снова.")

async def handle_router_callback(callback_query: CallbackQuery, bot: Bot):
    """Обработчик для кнопки 'Добавить роутер'."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вручную", callback_data="add_router_manually")],
        [InlineKeyboardButton(text="Сканировать", callback_data="scan_router_label")]
    ])
    
    await callback_query.message.answer("Выберите способ добавления роутера:", reply_markup=keyboard)
    await callback_query.answer()

async def start_router_registration(callback_query: CallbackQuery, state: FSMContext):
    """Начало регистрации роутера: спрашиваем серийный номер."""
    await callback_query.message.answer("Введите серийный номер роутера:")
    await state.set_state(RouterRegistration.waiting_for_serial_number)
    await callback_query.answer()

async def process_serial_number(message: types.Message, state: FSMContext):
    """Обработка серийного номера и запрос модели."""
    await state.update_data(serial_number=message.text)
    await message.answer("Введите модель роутера:")
    await state.set_state(RouterRegistration.waiting_for_model)

async def process_model(message: types.Message, state: FSMContext):
    """Обработка модели и запрос MAC-адреса."""
    await state.update_data(model=message.text)
    await message.answer("Введите MAC-адрес роутера:")
    await state.set_state(RouterRegistration.waiting_for_mac_address)

async def process_mac_address(message: types.Message, state: FSMContext):
    """Обработка MAC-адреса и запрос SKU."""
    # Сохраняем MAC-адрес в состояние FSM
    await state.update_data(mac_address=message.text.lower().replace(':', ''))  # Переводим MAC-адрес в нижний регистр и убираем двоеточия

    # Запрашиваем у пользователя SKU роутера
    await message.answer("Введите SKU роутера:")

    # Переключаемся на ожидание SKU
    await state.set_state(RouterRegistration.waiting_for_sku)


import secrets  # Добавим импорт для генерации токена

# В вашем файле admin.py

async def process_sku(message: types.Message, state: FSMContext):
    """Обработка SKU и завершение регистрации роутера."""
    # Получаем все данные, которые были сохранены в ходе диалога
    user_data = await state.get_data()
    serial_number = user_data['serial_number']
    model = user_data['model']
    mac_address = user_data['mac_address']
    sku = message.text  # Получаем SKU от пользователя

    # Логируем полученные данные
    logging.info(f"Серийный номер: {serial_number}, Модель: {model}, MAC-адрес: {mac_address}, SKU: {sku}")

    # Сформируем уникальный subdomain
    subdomain = f"{mac_address}.offonika.ru"
    
    # Генерируем токен аутентификации
    auth_token = secrets.token_hex(32)

    session = SessionLocal()
    try:
        # Добавляем новый роутер с введёнными данными в базу данных
        new_router = Router(
            serial_number=serial_number,
            model=model,
            mac_address=mac_address,
            sku=sku,  # Добавляем SKU
            subdomain=subdomain,
            auth_token=auth_token  # Добавляем токен аутентификации
        )
        session.add(new_router)
        session.commit()

        # Сообщаем об успешной регистрации роутера
        await message.answer(f"Роутер {model} с серийным номером {serial_number}, MAC-адресом {mac_address} и SKU {sku} успешно зарегистрирован.\nТокен: {auth_token}")
    except Exception as e:
        logging.error(f"Ошибка при регистрации роутера: {e}")
        await message.answer("Произошла ошибка при регистрации роутера.")
    finally:
        session.close()

    # Очищаем состояние FSM после завершения процесса
    await state.clear()




def register_handlers_admin(dp: Dispatcher):
    """Регистрация обработчиков команд для администратора."""
    dp.message.register(cmd_register_router, Command(commands=["register_router"]))
    dp.message.register(handle_router_image, F.content_type == types.ContentType.PHOTO)
    dp.callback_query.register(handle_router_callback, lambda c: c.data == "add_router")
    dp.callback_query.register(start_router_registration, lambda c: c.data == "add_router_manually")
    dp.message.register(process_serial_number, RouterRegistration.waiting_for_serial_number)
    dp.message.register(process_model, RouterRegistration.waiting_for_model)
    dp.message.register(process_mac_address, RouterRegistration.waiting_for_mac_address)
    dp.message.register(process_sku, RouterRegistration.waiting_for_sku)

