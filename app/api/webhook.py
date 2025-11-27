"""
Маршрут обработки входящих обновлений Telegram.
"""

from fastapi import APIRouter, Request
from aiogram import types
from app.bot.dispatcher import dp, bot

router = APIRouter()


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Получает обновления Telegram и передаёт их в диспетчер.
    """
    
    payload = await request.json()
    update = types.Update(**payload)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}