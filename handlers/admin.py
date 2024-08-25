from aiogram import types, Dispatcher

async def cmd_add_user(message: types.Message):
    # Здесь должен быть код для добавления пользователя в VPN
    await message.answer("Пользователь успешно добавлен.")

async def cmd_remove_user(message: types.Message):
    # Здесь должен быть код для удаления пользователя из VPN
    await message.answer("Пользователь успешно удален.")

def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_add_user, commands="add_user", is_chat_admin=True)
    dp.register_message_handler(cmd_remove_user, commands="remove_user", is_chat_admin=True)
