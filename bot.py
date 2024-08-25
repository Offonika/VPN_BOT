# bot.py

import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
import asyncio
from handlers.user import register_handlers_user, router as user_router
from handlers.admin import register_handlers_admin

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения из файла .env
load_dotenv()

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
dp = Dispatcher()  # Создаем диспетчер без аргументов

async def on_startup(dp: Dispatcher):
    """Функция инициализации, которая устанавливает команды бота."""
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Показать список команд"),
        BotCommand(command="/status", description="Проверить статус вашего VPN"),
        BotCommand(command="/add_user", description="Добавить пользователя в VPN"),
        BotCommand(command="/remove_user", description="Удалить пользователя из VPN")
    ])
    logging.info("Bot commands are set.")

def main():
    """Главная функция для запуска бота."""
    logging.info("Starting bot...")

    # Регистрация обработчиков
    register_handlers_user(user_router)
    register_handlers_admin(dp)

    # Включаем роутер в диспетчер
    dp.include_router(user_router)

    # Запускаем polling
    try:
        asyncio.run(dp.start_polling(bot, on_startup=on_startup))
    except Exception as e:
        logging.error(f"An error occurred during bot startup: {e}")

if __name__ == "__main__":
    main()

