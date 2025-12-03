import json

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from app.services.user import UserService
from app.services.internal import InternalSquadsService
from app.services.balance import BalanceService
from loguru import logger

router = Router()


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


@router.message(Command('balance'))
async def set_balance(message: Message):
    """
    Устанавливает баланс пользователя.
    Формат: /balance <telegram_id> <сумма>
    Пример: /balance 123456789 500
    """
    try:
        # Парсим команду
        parts = message.text.split()
        
        if len(parts) != 3:
            await message.answer(
                "❌ Неверный формат\n\n"
                "Использование: <code>/balance telegram_id сумма</code>\n"
                "Пример: <code>/balance 123456789 500</code>"
            )
            return
        
        telegram_id = int(parts[1])
        amount = float(parts[2])
        
        if amount < 0:
            await message.answer("❌ Сумма не может быть отрицательной")
            return
        
        # Устанавливаем баланс
        balance_service = BalanceService()
        new_balance = await balance_service.set_balance(telegram_id, amount)
        
        await message.answer(
            f"✅ Баланс установлен\n\n"
            f"Telegram ID: <code>{telegram_id}</code>\n"
            f"Новый баланс: <b>{new_balance:.2f}₽</b>"
        )
        
        logger.info(f'Баланс установлен: tg_id={telegram_id}, amount={amount}')
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат данных\n\n"
            "telegram_id и сумма должны быть числами"
        )
    except Exception:
        logger.exception(f'Ошибка установки баланса')
        await message.answer("❌ Произошла ошибка при установке баланса")