from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger

from app.core.logger.setup import setup_logger
from app.core.settings import config
from app.bot.dispatcher import bot
from app.bot.commands import set_default_commands
from app.api.telegram_webhook import router as telegram_webhook_router
from app.api.remnawave_webhook import router as remnawave_webhook_router
from app.api.yookassa_webhook import router as yookassa_webhook_router
from app.admin import setup_admin


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Форсирует HTTPS для админки."""
    
    async def dispatch(self, request: Request, call_next):
        request.scope["scheme"] = "https"
        response = await call_next(request)
        return response


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

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

app.include_router(telegram_webhook_router)
app.include_router(remnawave_webhook_router)
app.include_router(yookassa_webhook_router)

setup_admin(app)