from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.user import UserService
from app.services.client import PanelError
from loguru import logger

router = Router()


@router.message(Command('devices'))
async def show_devices_handler(message: Message):
    """Показывает список подключенных устройств."""
    service = UserService()
    telegram_id = message.from_user.id

    try:
        user = await service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer('❌ Пользователь не найден')
            return

        devices = await service.get_user_devices(user.panel_uuid)
        await service.update_hwid_count(telegram_id, len(devices))

        limit = user.subscription.hwid_limit or '∞'
        text = f"📱 <b>Мои устройства: {len(devices)}/{limit}</b>\n\n"

        if not devices:
            text += "Устройства не подключены\n\n"
            text += "Чтобы подключить устройство, импортируй подписку в VPN клиент"
        else:
            for idx, device in enumerate(devices, 1):
                hwid = device.get('hwid', 'unknown')
                platform = device.get('platform') or 'Неизвестная платформа'
                device_model = device.get('deviceModel') or 'Неизвестное устройство'
                created_at = device.get('createdAt', '')
                
                text += f"{idx}. <b>{device_model}</b> ({platform})\n"
                text += f"   ID: <code>{hwid}</code>\n"
                if created_at:
                    text += f"   Подключено: {created_at[:10]}\n"
                text += "\n"

            text += f"Для удаления используй:\n"
            text += f"<code>/delete [ID устройства]</code>\n"
            text += f"<code>/delete_all</code> - удалить все"

        await message.answer(text)
        logger.info(f'Пользователь tg_id={telegram_id} просмотрел устройства: {len(devices)}/{limit}')

    except PanelError as e:
        logger.error(f'Ошибка панели для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Не удалось получить список устройств')

    except Exception:
        logger.exception(f'Ошибка при получении устройств tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка')


@router.message(Command('delete'))
async def delete_device_handler(message: Message):
    """Удаляет конкретное устройство по ID."""
    service = UserService()
    telegram_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            '❌ Укажи ID устройства\n\n'
            'Пример: <code>/delete abc123def456</code>\n\n'
            'Узнать ID можно командой /devices'
        )
        return

    device_id = args[1].strip()

    try:
        user = await service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer('❌ Пользователь не найден')
            return

        await service.delete_user_device(user.panel_uuid, device_id)

        devices = await service.get_user_devices(user.panel_uuid)
        await service.update_hwid_count(telegram_id, len(devices))

        await message.answer(
            f'✅ Устройство удалено\n\n'
            f'Осталось устройств: {len(devices)}/{user.subscription.hwid_limit or "∞"}'
        )
        logger.info(f'Пользователь tg_id={telegram_id} удалил устройство {device_id}')

    except PanelError as e:
        logger.error(f'Ошибка удаления устройства для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Не удалось удалить устройство. Проверь ID')

    except Exception:
        logger.exception(f'Ошибка при удалении устройства tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка')


@router.message(Command('delete_all'))
async def delete_all_devices_handler(message: Message):
    """Удаляет все устройства пользователя."""
    service = UserService()
    telegram_id = message.from_user.id

    try:
        user = await service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer('❌ Пользователь не найден')
            return

        await service.reset_user_devices(user.panel_uuid)
        await service.update_hwid_count(telegram_id, 0)

        await message.answer('✅ Все устройства удалены')
        logger.info(f'Пользователь tg_id={telegram_id} удалил все устройства')

    except PanelError as e:
        logger.error(f'Ошибка сброса устройств для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Не удалось удалить устройства')

    except Exception:
        logger.exception(f'Ошибка при сбросе устройств tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка')