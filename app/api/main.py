from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.logger.setup import setup_logger
from app.core.settings import config
from app.bot.dispatcher import bot
from app.bot.commands import set_default_commands
from app.api.telegram_webhook import router as telegram_webhook_router
from app.api.remnawave_webhook import router as remnawave_webhook_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(config.TELEGRAM_WEBHOOK)
    logger.info('Вебхук установлен')
    
    await set_default_commands(bot)
     
    yield

    logger.info('Удаление вебхука Telegram')
    await bot.delete_webhook()

    logger.info('Закрытие сессии бота')
    await bot.session.close()

    logger.info('Приложение завершило работу')


setup_logger()

app = FastAPI(lifespan=lifespan)
app.include_router(telegram_webhook_router)
app.include_router(remnawave_webhook_router)