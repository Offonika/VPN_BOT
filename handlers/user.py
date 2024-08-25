from aiogram import types, Router
from aiogram.filters import Command

router = Router()

async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в VPN бот! Введите /help для списка доступных команд.")

async def cmd_help(message: types.Message):
    await message.answer("/start - Начать работу\n/help - Показать это сообщение\n/status - Проверить статус вашего VPN")

async def cmd_status(message: types.Message):
    # Здесь должен быть код для проверки статуса пользователя в VPN
    await message.answer("Ваш VPN активен.")

def register_handlers_user(router: Router):
    router.message.register(cmd_start, Command(commands=["start"]))
    router.message.register(cmd_help, Command(commands=["help"]))
    router.message.register(cmd_status, Command(commands=["status"]))
