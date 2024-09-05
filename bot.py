# bot.py

import os
import logging
import asyncio
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from handlers.user import register_handlers_user, router as user_router
from handlers.admin import register_handlers_admin
from middlewares.middleware import BotContextMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения из файла .env
load_dotenv(dotenv_path='/opt/VPN_BOT/.env')

# Проверка значения переменной окружения
database_url = 'postgresql+psycopg2://vpn_bot_user:12345@147.45.232.192:5432/vpn_db'

print(f"DATABASE_URL: {database_url}")

telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
print(f"TELEGRAM_API_TOKEN: {telegram_api_token}")

def get_api_token() -> str:
    """Функция для получения и проверки токена API из переменных окружения."""
    token = os.getenv('TELEGRAM_API_TOKEN')
    if not token or token.strip() == "":
        raise ValueError("TELEGRAM_API_TOKEN is not set in environment variables or .env file")
    return token

# Получение токена API
API_TOKEN = get_api_token()

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация middleware
dp.update.middleware(BotContextMiddleware())  # Добавляем middleware

async def on_startup(bot: Bot):
    """Функция инициализации, которая устанавливает команды бота."""
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Показать список команд"),
        BotCommand(command="/status", description="Проверить статус вашего VPN"),
        BotCommand(command="/get_vpn_key", description="Получить VPN ключ"),
        BotCommand(command="/pay_vpn", description="Оплатить VPN"),
        BotCommand(command="/get_instruction", description="Получить инструкцию"),
        BotCommand(command="/add_user", description="Добавить пользователя в VPN"),
        BotCommand(command="/remove_user", description="Удалить пользователя из VPN"),
        BotCommand(command="/register_router", description="Зарегистрировать новый роутер")
    ]
    try:
        await bot.set_my_commands(commands)
        logging.info("Bot commands are set.")
    except Exception as e:
        logging.error(f"Error setting bot commands: {e}")

async def start_bot():
    """Функция запуска бота."""
    logging.info("Starting bot...")

    # Удаляем существующие обработчики сигналов и добавляем новые
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.remove_signal_handler(sig)
        except NotImplementedError:
            pass

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(loop.shutdown_asyncgens()))

    # Регистрация обработчиков
    register_handlers_user(user_router)
    register_handlers_admin(dp)

    dp.include_router(user_router)

    try:
        await dp.start_polling(bot, on_startup=on_startup)
    except Exception as e:
        logging.error(f"An error occurred during bot startup: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
