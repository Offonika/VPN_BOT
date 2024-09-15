import os
import asyncio
import signal
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from middlewares.middleware import BotContextMiddleware  # Ваше middleware
from aiogram import Router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из файла .env
load_dotenv(dotenv_path='/opt/VPN_BOT/.env')

def get_api_token() -> str:
    """Функция для получения и проверки токена API из переменных окружения."""
    token = os.getenv('TELEGRAM_API_TOKEN')
    if not token or token.strip() == "":
        logger.error("TELEGRAM_API_TOKEN не установлен в переменных окружения или файле .env")
        raise ValueError("TELEGRAM_API_TOKEN не установлен в переменных окружения или файле .env")
    return token

# Получение токена API
API_TOKEN = get_api_token()

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация middleware
dp.update.middleware(BotContextMiddleware())  # Ваше middleware

# Импорт хендлеров
from handlers.user import register_handlers_user, router as user_router
from handlers.admin import register_handlers_admin
from handlers.store import router as store_router  # Импорт роутера для магазина

async def on_startup(bot: Bot):
    """Функция инициализации, которая устанавливает команды бота."""
    logger.info("Установка команд бота...")
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
        BotCommand(command="/connect_vpn", description="Подключить VPN"),
        BotCommand(command="/store", description="Магазин роутеров")  # Добавляем команду для магазина
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Команды бота установлены.")
    except Exception as e:
        logger.error(f"Ошибка при установке команд бота: {e}")

async def start_bot():
    """Функция запуска бота."""
    logger.info("Запуск бота...")
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.remove_signal_handler(sig)
        except NotImplementedError:
            pass
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(loop.shutdown_asyncgens()))

    # Создание и регистрация роутеров
    register_handlers_user(user_router)  # Регистрируем хендлеры пользователя
    dp.include_router(user_router)       # Включаем роутер пользователя

    # Создаем админский роутер и регистрируем хендлеры администратора
    admin_router = Router()
    register_handlers_admin(admin_router)
    dp.include_router(admin_router)      # Включаем роутер администратора

    dp.include_router(store_router)      # Включаем роутер магазина

    # Запуск бота
    try:
        await dp.start_polling(bot, on_startup=on_startup)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(start_bot())


