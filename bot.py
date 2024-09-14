import os
import asyncio
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from logger import logger  # Импорт логгера
from handlers.user import register_handlers_user, router as user_router
from handlers.admin import register_handlers_admin
from middlewares.middleware import BotContextMiddleware
from handlers.user import cmd_start, cmd_help, cmd_status, cmd_download_config, cmd_get_qr_code, cmd_connect_vpn
from aiogram.filters import Command
from handlers.user import handle_get_vpn_key
from handlers.user import cmd_get_qr_code
from handlers.user import handle_get_qr_code
from handlers.user import handle_download_config
from handlers.user import handle_get_instruction
from handlers.user import process_pay_command
from handlers.user import handle_go_back
from handlers.user import process_vpn_choice
from aiogram import F
from aiogram import types
from handlers.payments import handle_pre_checkout_query, handle_successful_payment
from handlers.user import cmd_balance
from handlers.user import process_pay_balance

from config import YKASSA_PROVIDER_TOKEN, VPN_ENDPOINT

# Загрузка переменных окружения из файла .env
load_dotenv(dotenv_path='/opt/VPN_BOT/.env')

# Проверка значения переменной окружения
database_url = 'postgresql+psycopg2://vpn_bot_user:12345@147.45.232.192:5432/vpn_db'
logger.info(f"DATABASE_URL: {database_url}")

telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
logger.info(f"TELEGRAM_API_TOKEN: {telegram_api_token}")

def get_api_token() -> str:
    """Функция для получения и проверки токена API из переменных окружения."""
    token = os.getenv('TELEGRAM_API_TOKEN')
    if not token or token.strip() == "":
        logger.error("TELEGRAM_API_TOKEN is not set in environment variables or .env file")
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
    logger.info("Setting bot commands...")
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Показать список команд"),
        BotCommand(command="/status", description="Проверить статус вашего VPN"),
        BotCommand(command="/get_vpn_key", description="Получить VPN ключ"),
        BotCommand(command="/pay_vpn", description="Оплатить VPN"),
        BotCommand(command="/get_instruction", description="Получить инструкцию"),
        BotCommand(command="/register_router", description="Зарегистрировать новый роутер"),
        BotCommand(command="/download_config", description="Скачать конфигурацию"),
        BotCommand(command="/get_qr_code", description="Получить QR код"),
        BotCommand(command="/connect_vpn", description="Подключить VPN")
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Bot commands are set.")
    except Exception as e:
        logger.error(f"Error setting bot commands: {e}")

def register_handlers_user(router):
    """Регистрация всех хендлеров для пользователя."""
    router.message.register(cmd_start, Command(commands=["start"]))
    router.message.register(cmd_help, Command(commands=["help"]))
    router.message.register(cmd_status, Command(commands=["status"]))
    router.message.register(cmd_download_config, Command(commands=["download_config"]))
    router.message.register(cmd_get_qr_code, Command(commands=["get_qr_code"]))
    router.message.register(cmd_connect_vpn, Command(commands=["connect_vpn"]))
    router.callback_query.register(handle_get_vpn_key, lambda c: c.data == "get_vpn_key")
    router.callback_query.register(handle_get_qr_code, lambda c: c.data == "get_qr_code")
    router.callback_query.register(handle_download_config, lambda c: c.data == "download_config")
    router.callback_query.register(handle_get_instruction, lambda c: c.data == "get_instruction")
    router.callback_query.register(process_pay_command, lambda c: c.data == "pay_vpn")
    router.callback_query.register(handle_go_back, lambda c: c.data == "go_back")
    router.callback_query.register(process_vpn_choice, lambda c: c.data in ["choose_vpn_protocol", "wg_vpn", "ocserv_vpn", "ss_vpn"])
    router.pre_checkout_query.register(handle_pre_checkout_query)
    router.message.register(handle_successful_payment, F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
    router.message.register(cmd_balance, Command(commands=["balance"]))
    router.callback_query.register(process_pay_balance, lambda c: c.data == "pay")  # Для кнопки
    router.message.register(process_pay_balance, Command(commands=["pay"]))  # Для команды /pay

async def start_bot():
    """Функция запуска бота."""
    logger.info("Starting bot...")

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
        logger.error(f"An error occurred during bot startup: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
