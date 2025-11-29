from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    """
    Устанавливает команды с меню.
    """
    
    commands = [
        BotCommand(command='start', description='Создать подписку'),
        BotCommand(command='users', description='Посмотреть всех клиентов'),
        BotCommand(command='internals', description='Посмотреть все внутренние сквады'),
        BotCommand(command='admin', description='Посмотреть JWT токен админа'),
    ]
    
    await bot.set_my_commands(commands)