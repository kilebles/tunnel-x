import json

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile


from app.services.client import PanelClient
from app.services.user import UserService
from app.services.internal import InternalSquadsService

router = Router()


@router.message(Command('admin'))
async def test_panel(message: Message):
    client = PanelClient()
    
    token = await client.auth.login()
    await message.answer(f'Token received: {token}')


@router.message(Command('users'))
async def test_clients(message: Message):
    service = UserService()
    data = await service.list_users()

    content = json.dumps(data, ensure_ascii=False, indent=2).encode()

    file = BufferedInputFile(
        file=content,
        filename='users.json'
    )

    await message.answer_document(
        document=file,
        caption='Список пользователей'
    )


@router.message(Command('internals'))
async def test_internals(message: Message):
    service = InternalSquadsService()
    data = await service.get_internal_squads()

    content = json.dumps(data, ensure_ascii=False, indent=2).encode()

    file = BufferedInputFile(file=content, filename='internal_squads.json')

    await message.answer_document(
        document=file,
        caption='Внутренние сквады'
    )