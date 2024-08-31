# handlers/admin.py

from aiogram import types, Dispatcher
from aiogram.filters import Command
from db.database import SessionLocal
from db.models import VpnClient, Router
from utils.vpn_config import add_vpn_user, remove_vpn_user, restart_wireguard
from utils.ddns import update_dns  # Импортируем функцию обновления DNS
import logging

async def is_user_admin(message: types.Message) -> bool:
    """Проверяет, является ли пользователь администратором в чате."""
    chat_administrators = await message.bot.get_chat_administrators(message.chat.id)
    user_id = message.from_user.id
    return any(admin.user.id == user_id for admin in chat_administrators)

async def cmd_add_user(message: types.Message):
    """Обработчик команды /add_user. Добавляет пользователя в VPN по Telegram ID."""
    if not await is_user_admin(message):
        await message.answer("Эта команда доступна только администраторам.")
        return

    telegram_id = message.get_args()
    if not telegram_id:
        await message.answer("Пожалуйста, укажите Telegram ID пользователя.")
        return

    session = SessionLocal()
    try:
        client = session.query(VpnClient).filter(VpnClient.telegram_id == telegram_id).first()
        if client:
            success = add_vpn_user(client.public_key, client.address)
            if success:
                await message.answer(f"Пользователь {telegram_id} успешно добавлен в VPN.")
                restart_wireguard()
            else:
                await message.answer("Не удалось добавить пользователя в VPN.")
        else:
            await message.answer("Пользователь с таким ID не найден.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя в VPN: {e}")
        await message.answer("Произошла ошибка при добавлении пользователя в VPN.")
    finally:
        session.close()

async def cmd_remove_user(message: types.Message):
    """Обработчик команды /remove_user. Удаляет пользователя из VPN по Telegram ID."""
    if not await is_user_admin(message):
        await message.answer("Эта команда доступна только администраторам.")
        return

    telegram_id = message.get_args()
    if not telegram_id:
        await message.answer("Пожалуйста, укажите Telegram ID пользователя.")
        return

    session = SessionLocal()
    try:
        client = session.query(VpnClient).filter(VpnClient.telegram_id == telegram_id).first()
        if client:
            success = remove_vpn_user(client.public_key)
            if success:
                await message.answer(f"Пользователь {telegram_id} успешно удален из VPN.")
                restart_wireguard()
            else:
                await message.answer("Не удалось удалить пользователя из VPN.")
        else:
            await message.answer("Пользователь с таким ID не найден.")
    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя из VPN: {e}")
        await message.answer("Произошла ошибка при удалении пользователя из VPN.")
    finally:
        session.close()

async def cmd_register_router(message: types.Message):
    """Обработчик команды /register_router. Регистрирует новый роутер через сканирование штрихкода."""
    if not await is_user_admin(message):
        await message.answer("Эта команда доступна только администраторам.")
        return

    # Логика сканирования штрихкода и получения данных о роутере
    # Например, используем message.photo для получения изображения штрихкода
    # и потом используем внешнюю библиотеку для распознавания

    router_info = extract_router_info_from_qrcode(message.photo)
    if not router_info:
        await message.answer("Не удалось распознать данные роутера. Пожалуйста, попробуйте снова.")
        return

    session = SessionLocal()
    try:
        # Добавляем роутер в базу данных
        new_router = Router(
            serial_number=router_info['serial_number'],
            model=router_info['model'],
            ip_address=router_info['ip_address'],  # или другой метод определения IP
            user_id=router_info['user_id']
        )
        session.add(new_router)
        session.commit()

        # Обновляем DNS-запись для роутера
        success = update_dns(router_info['hostname'], router_info['ip_address'])
        if success:
            await message.answer(f"Роутер {router_info['hostname']} успешно зарегистрирован и DNS обновлен.")
        else:
            await message.answer("Не удалось обновить DNS для нового роутера.")

    except Exception as e:
        logging.error(f"Ошибка при регистрации роутера: {e}")
        await message.answer("Произошла ошибка при регистрации роутера.")
    finally:
        session.close()

def register_handlers_admin(dp: Dispatcher):
    """Регистрация обработчиков команд для администратора."""
    dp.message.register(cmd_add_user, Command(commands=["add_user"]))
    dp.message.register(cmd_remove_user, Command(commands=["remove_user"]))
    dp.message.register(cmd_register_router, Command(commands=["register_router"]))  # Регистрация нового обработчика
