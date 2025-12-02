from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.device import DeviceService
from app.services.client import PanelError
from loguru import logger

router = Router()


@router.message(Command('devices'))
async def show_devices_handler(message: Message):
    """Показывает список подключенных устройств."""
    service = DeviceService()
    telegram_id = message.from_user.id

    try:
        devices, limit = await service.get_devices(telegram_id)
        
        text = f"📱 <b>Мои устройства: {len(devices)}/{limit or '∞'}</b>\n\n"

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
    service = DeviceService()
    telegram_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            '❌ Укажи ID устройства\n\n'
            'Пример: <code>/delete abc123def456</code>\n\n'
            'Узнать ID можно командой /devices'
        )
        return

    hwid = args[1].strip()

    try:
        remaining, limit = await service.delete_device(telegram_id, hwid)

        await message.answer(
            f'✅ Устройство удалено\n\n'
            f'Осталось устройств: {remaining}/{limit or "∞"}'
        )
        logger.info(f'Пользователь tg_id={telegram_id} удалил устройство {hwid}')

    except ValueError as e:
        await message.answer(f'❌ {e}')
    
    except PanelError as e:
        logger.error(f'Ошибка удаления устройства для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Не удалось удалить устройство. Проверь ID')

    except Exception:
        logger.exception(f'Ошибка при удалении устройства tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка')


@router.message(Command('delete_all'))
async def delete_all_devices_handler(message: Message):
    """Удаляет все устройства пользователя."""
    service = DeviceService()
    telegram_id = message.from_user.id

    try:
        await service.reset_devices(telegram_id)
        await message.answer('✅ Все устройства удалены')
        logger.info(f'Пользователь tg_id={telegram_id} удалил все устройства')

    except ValueError as e:
        await message.answer(f'❌ {e}')
    
    except PanelError as e:
        logger.error(f'Ошибка сброса устройств для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Не удалось удалить устройства')

    except Exception:
        logger.exception(f'Ошибка при сбросе устройств tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка')