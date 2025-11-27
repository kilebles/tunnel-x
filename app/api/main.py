import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.settings import config
from app.bot.dispatcher import bot
from app.bot.commands import set_default_commands
from app.api.webhook import router as webhook_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Устанавливает вебхук и команды, 
    удаляет вебхук и закрывает соединение.
    """
    
    logger.info("Установка вебхука Telegram")

    await bot.set_webhook(config.TELEGRAM_WEBHOOK)
    await set_default_commands(bot)

    logger.info("Вебхук установлен")
    yield

    logger.info("Удаление вебхука Telegram")
    await bot.delete_webhook()

    logger.info("Закрытие сессии бота")
    await bot.session.close()

    logger.info("Приложение завершило работу")


app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router)