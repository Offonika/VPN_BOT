# handlers/user.py

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from db.database import SessionLocal
from db.models import User, VpnClient
from utils.vpn_config import generate_vpn_keys, generate_vpn_config, restart_wireguard
from utils.ip_manager import get_free_ip
from utils.qr_generator import generate_qr_code
from aiohttp import ClientConnectionError
import asyncio
import logging

router = Router()

async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подключить VPN", callback_data="get_vpn_key")]
    ])
    await message.answer("Добро пожаловать в VPN бот! Нажмите кнопку ниже, чтобы подключиться к VPN.", reply_markup=keyboard)

async def cmd_help(message: types.Message):
    """Обработчик команды /help."""
    await message.answer("/start - Начать работу\n/help - Показать это сообщение\n/status - Проверить статус вашего VPN")

async def cmd_status(message: types.Message):
    """Обработчик команды /status."""
    await message.answer("Ваш VPN активен.")

async def handle_get_vpn_key(callback_query: types.CallbackQuery):
    """Обработчик нажатия кнопки "Подключить VPN". Генерирует ключи, конфигурацию и QR-код."""
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            # Регистрация нового пользователя, если его нет в базе данных
            user = User(
                telegram_id=telegram_id,
                username=callback_query.from_user.username or '',
                full_name=callback_query.from_user.full_name or '',
                # Добавьте другие необходимые поля, если нужно
            )
            session.add(user)
            session.commit()
            await callback_query.message.answer("Вы были зарегистрированы в системе.")
        
        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()
        if client:
            # Отправка кнопок для существующего VPN клиента
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="QR код", callback_data="get_qr_code")],
                [InlineKeyboardButton(text="Скачать конфигурацию", callback_data="download_config")],
                [InlineKeyboardButton(text="Инструкция", callback_data="get_instruction")]
            ])
            await callback_query.message.answer("Вы уже зарегистрированы в системе VPN. Выберите действие:", reply_markup=keyboard)
        else:
            private_key, public_key = generate_vpn_keys()
            ip_address = get_free_ip(session)

            new_client = VpnClient(
                user_id=user.id,
                private_key=private_key,
                public_key=public_key,
                address=ip_address,
                dns="8.8.8.8",
                allowed_ips="0.0.0.0/0",
                endpoint="147.45.232.192:443"
            )

            session.add(new_client)
            session.commit()
            logging.info(f"New VPN client added for user {telegram_id}")

            # Генерация конфигурационного файла
            config_file = generate_vpn_config(new_client)
            with open(config_file, 'r') as file:
                config_content = file.read()

            qr_code_path = generate_qr_code(config_content, client_id=telegram_id)

            # Отправка кнопок после успешного создания VPN клиента
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="QR код", callback_data="get_qr_code")],
                [InlineKeyboardButton(text="Скачать конфигурацию", callback_data="download_config")],
                [InlineKeyboardButton(text="Инструкция", callback_data="get_instruction")]
            ])
            await callback_query.message.answer("VPN клиент успешно создан. Выберите действие:", reply_markup=keyboard)

            restart_wireguard()

    except Exception as e:
        logging.error(f"An error occurred while handling VPN key request: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.")
    finally:
        session.close()
        await callback_query.answer()

async def handle_get_qr_code(callback_query: types.CallbackQuery):
    """Обработчик для кнопки 'QR код'."""
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()
        
        if client:
            qr_code_path = generate_qr_code(client.config_text, client_id=telegram_id)
            attempts = 3  # Количество попыток
            for attempt in range(attempts):
                try:
                    await callback_query.message.answer_photo(InputFile(qr_code_path), caption="Вот ваш QR-код для подключения к VPN.")
                    break  # Выход из цикла, если отправка успешна
                except ClientConnectionError as e:
                    logging.error(f"ClientConnectionError on attempt {attempt + 1}: {e}")
                    if attempt < attempts - 1:
                        await asyncio.sleep(2 ** (attempt + 1))  # Увеличиваем время ожидания перед следующей попыткой
                    else:
                        await callback_query.message.answer("Не удалось отправить QR-код. Попробуйте позже.")
        else:
            await callback_query.message.answer("VPN клиент не найден. Пожалуйста, сначала зарегистрируйтесь.")

    except Exception as e:
        logging.error(f"An error occurred while handling QR code request: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса.")
    finally:
        session.close()
        await callback_query.answer()

async def handle_download_config(callback_query: types.CallbackQuery):
    """Обработчик для кнопки 'Скачать конфигурацию'."""
    telegram_id = callback_query.from_user.id
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            await callback_query.message.answer("Пользователь не найден. Пожалуйста, зарегистрируйтесь сначала.")
            return

        client = session.query(VpnClient).filter(VpnClient.user_id == user.id).first()

        if client:
            config_file = generate_vpn_config(client)
            await callback_query.message.answer_document(InputFile(config_file), caption="Вот ваш конфигурационный файл.")
        else:
            await callback_query.message.answer("VPN клиент не найден. Пожалуйста, сначала зарегистрируйтесь.")

    except Exception as e:
        logging.error(f"An error occurred while handling configuration download request: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего запроса.")
    finally:
        session.close()
        await callback_query.answer()

async def handle_get_instruction(callback_query: types.CallbackQuery):
    """Обработчик для кнопки 'Инструкция'."""
    await callback_query.message.answer("Для подключения к VPN, следуйте этим инструкциям...")
    await callback_query.answer()

def register_handlers_user(router: Router):
    """Регистрация обработчиков команд для пользователя."""
    router.message.register(cmd_start, Command(commands=["start"]))
    router.message.register(cmd_help, Command(commands=["help"]))
    router.message.register(cmd_status, Command(commands=["status"]))
    router.callback_query.register(handle_get_vpn_key, lambda c: c.data == "get_vpn_key")
    router.callback_query.register(handle_get_qr_code, lambda c: c.data == "get_qr_code")
    router.callback_query.register(handle_download_config, lambda c: c.data == "download_config")
    router.callback_query.register(handle_get_instruction, lambda c: c.data == "get_instruction")
