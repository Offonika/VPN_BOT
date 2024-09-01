# middlewares/middleware.py

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class BotContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict) -> any:
        # Получаем объект бота из данных, передаваемых в middleware
        bot = data.get('bot')
        if bot:
            data['bot'] = bot
        return await handler(event, data)
