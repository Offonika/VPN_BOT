# bot.py

import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
from handlers.user import register_handlers_user, router  # Импортируем ваш Router и функцию регистрации

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
dp = Dispatcher()  # Создаем диспетчер

# Регистрация обработчиков
register_handlers_user(router)

async def main():
    """Главная функция для запуска бота."""
    try:
        logging.info("Starting bot...")
        # Включаем роутер в диспетчер
        dp.include_router(router)
        # Запускаем polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
