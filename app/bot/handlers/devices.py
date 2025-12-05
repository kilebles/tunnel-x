from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.services.user import UserService
from app.services.device import DeviceService
from app.services.message import MessageService
from app.services.client import PanelError
from app.bot.keyboards.devices import build_devices_menu, get_devices_menu_text
from app.bot.keyboards.main_menu import build_main_menu, get_main_menu_text
from app.bot.keyboards.callback_data import MainMenuCallback, DeviceCallback
from loguru import logger

router = Router()


async def safe_answer(callback: CallbackQuery, text: str | None = None, show_alert: bool = False):
    """Безопасный ответ на callback query."""
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest as e:
        if 'query is too old' in str(e).lower() or 'query' in str(e).lower():
            logger.debug(f'Callback query устарел: {e}')
        else:
            raise


@router.callback_query(MainMenuCallback.filter(F.action == 'devices'))
async def show_devices_menu(callback: CallbackQuery, callback_data: MainMenuCallback):
    """Показывает меню управления устройствами."""
    
    device_service = DeviceService()
    message_service = MessageService()
    telegram_id = callback.from_user.id
    
    try:
        devices, limit = await device_service.get_devices(telegram_id)
        
        text = get_devices_menu_text(devices, limit)
        keyboard = build_devices_menu(devices, limit)
        
        await message_service.update_or_send_menu(
            bot=callback.bot,
            telegram_id=telegram_id,
            text=text,
            keyboard=keyboard
        )
        await safe_answer(callback)
        logger.info(f'Открыто меню устройств для tg_id={telegram_id}')
        
    except PanelError as e:
        logger.error(f'Ошибка панели для tg_id={telegram_id}: {e}')
        await safe_answer(callback, '⚠️ Не удалось получить список устройств', show_alert=True)
        
    except Exception:
        logger.exception(f'Ошибка открытия меню устройств tg_id={telegram_id}')
        await safe_answer(callback, '❌ Произошла ошибка', show_alert=True)


@router.callback_query(DeviceCallback.filter(F.action == 'info'))
async def device_info(callback: CallbackQuery, callback_data: DeviceCallback):
    """Показывает информацию об устройстве."""
    device_service = DeviceService()
    telegram_id = callback.from_user.id
    hwid = callback_data.hwid
    
    if not hwid:
        await safe_answer(callback, "❌ Ошибка: ID устройства не найден", show_alert=True)
        return
    
    try:
        devices, _ = await device_service.get_devices(telegram_id)
        
        device = next((d for d in devices if d.get('hwid') == hwid), None)
        
        if not device:
            await safe_answer(callback, "❌ Устройство не найдено", show_alert=True)
            return
        
        platform = device.get('platform') or 'Неизвестно'
        os_version = device.get('osVersion') or 'Неизвестно'
        device_model = device.get('deviceModel') or 'Неизвестно'
        created_at = device.get('createdAt', '')[:10] if device.get('createdAt') else 'Неизвестно'
        
        info_text = (
            f"📱 {device_model}\n"
            f"💻 Платформа: {platform}\n"
            f"📟 ОС: {os_version}\n"
            f"📅 Подключено: {created_at}\n"
        )
        
        await safe_answer(callback, info_text, show_alert=True)
        
    except Exception:
        logger.exception(f'Ошибка получения информации об устройстве tg_id={telegram_id}')
        await safe_answer(callback, "❌ Произошла ошибка", show_alert=True)


@router.callback_query(DeviceCallback.filter(F.action == 'delete'))
async def delete_device_callback(callback: CallbackQuery, callback_data: DeviceCallback):
    """Удаляет устройство по hwid."""
    
    device_service = DeviceService()
    message_service = MessageService()
    telegram_id = callback.from_user.id
    hwid = callback_data.hwid
    
    if not hwid:
        await safe_answer(callback, '❌ Ошибка: ID устройства не найден', show_alert=True)
        return
    
    try:
        remaining, limit = await device_service.delete_device(telegram_id, hwid)
        
        devices, limit = await device_service.get_devices(telegram_id)
        text = get_devices_menu_text(devices, limit)
        keyboard = build_devices_menu(devices, limit)
        
        await message_service.update_or_send_menu(
            bot=callback.bot,
            telegram_id=telegram_id,
            text=text,
            keyboard=keyboard
        )
        await safe_answer(callback, f'✅ Устройство удалено. Осталось: {remaining}', show_alert=True)
        
        logger.info(f'Устройство {hwid} удалено для tg_id={telegram_id}')
        
    except ValueError as e:
        await safe_answer(callback, f'❌ {e}', show_alert=True)
        
    except PanelError as e:
        logger.error(f'Ошибка удаления устройства для tg_id={telegram_id}: {e}')
        await safe_answer(callback, '⚠️ Не удалось удалить устройство', show_alert=True)
        
    except Exception:
        logger.exception(f'Ошибка удаления устройства tg_id={telegram_id}')
        await safe_answer(callback, '❌ Произошла ошибка', show_alert=True)


@router.callback_query(MainMenuCallback.filter(F.action == 'back'))
async def back_to_main_menu(callback: CallbackQuery, callback_data: MainMenuCallback):
    """Возвращает в главное меню."""
    
    user_service = UserService()
    message_service = MessageService()
    telegram_id = callback.from_user.id
    
    try:
        user = await user_service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await safe_answer(callback, '❌ Пользователь не найден', show_alert=True)
            return
        
        text = get_main_menu_text(user)
        keyboard = build_main_menu(user)
        
        await message_service.update_or_send_menu(
            bot=callback.bot,
            telegram_id=telegram_id,
            text=text,
            keyboard=keyboard
        )
        await safe_answer(callback)
        logger.info(f'Возврат в главное меню для tg_id={telegram_id}')
        
    except Exception:
        logger.exception(f'Ошибка возврата в главное меню tg_id={telegram_id}')
        await safe_answer(callback, '❌ Произошла ошибка', show_alert=True)