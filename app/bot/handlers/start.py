from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.client import PanelClient

router = Router()


@router.message(Command('paneltest'))
async def test_panel(message: Message):
    client = PanelClient()
    
    token = await client.auth.login()
    await message.answer(f'Token received: {token}')