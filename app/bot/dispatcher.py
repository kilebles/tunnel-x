"""
Инициализация бота и диспетчера.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties

from app.core.settings import config
from app.bot.router import router

bot = Bot(
    token=config.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode='HTML')
)

storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)
dp.include_router(router)