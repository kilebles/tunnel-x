from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    """
    Устанавливает команды с меню.
    """
    commands = [
        BotCommand(command='start', description='В туннель 🚶🏻'),
        BotCommand(command='devices', description='Мои устройства'),
        BotCommand(command='delete', description='Удалить устройство "id"'),
        BotCommand(command='delete_all', description='Удалить все устройства'),
        BotCommand(command='users', description='Посмотреть всех клиентов'),
        BotCommand(command='internals', description='Посмотреть все внутренние сквады'),
    ]
    
    await bot.set_my_commands(commands)