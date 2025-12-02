"""
Подключение роутов.
"""

from aiogram import Router
from app.bot.handlers.start import router as start_router
from app.bot.handlers.devices import router as devices_router
from app.bot.handlers.admin import router as admin_router

router = Router()

router.include_router(start_router)
router.include_router(devices_router)
router.include_router(admin_router)