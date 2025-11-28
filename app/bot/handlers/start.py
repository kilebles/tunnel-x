import json

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile


from app.services.client import PanelClient
from app.services.users import UsersService
from app.services.internal import InternalSquadsService

router = Router()


@router.message(Command('paneltest'))
async def test_panel(message: Message):
    client = PanelClient()
    
    token = await client.auth.login()
    await message.answer(f'Token received: {token}')


@router.message(Command('users'))
async def test_clients(message: Message):
    service = UsersService()
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
    

@router.message(Command('create'))
async def create_user_handler(message: Message):
    service = UsersService()

    username = message.from_user.username or f'user_{message.from_user.id}'
    expire_at = '2099-01-01T00:00:00.000Z'  # потом передать время

    data = await service.create_user(username, expire_at)

    if 'response' not in data:
        await message.answer('Чел, успокойся у тебя уже есть хапка, за вторую придется заплатить')
        return

    url = data['response']['subscriptionUrl']

    await message.answer(f"<a href='{url}'>лови хапку</a>")