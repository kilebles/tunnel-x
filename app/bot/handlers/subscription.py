from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.subscription import build_subscription_menu, get_subscription_menu_text
from app.bot.keyboards.callback_data import MainMenuCallback, SubscriptionCallback
from loguru import logger

router = Router()


@router.callback_query(MainMenuCallback.filter(F.action == 'upgrade'))
async def show_subscription_menu(callback: CallbackQuery, callback_data: MainMenuCallback):
    """Открывает меню выбора тарифа."""
    await callback.answer()
    
    try:
        # По умолчанию: 2 устройства, 30 дней
        text = get_subscription_menu_text(devices=2, days=30)
        keyboard = build_subscription_menu(devices=2, days=30)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        logger.info(f'Открыто меню подписки для tg_id={callback.from_user.id}')
        
    except Exception:
        logger.exception(f'Ошибка открытия меню подписки tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(SubscriptionCallback.filter(F.action == 'select_days'))
async def select_days(callback: CallbackQuery, callback_data: SubscriptionCallback):
    """Обрабатывает выбор срока."""
    await callback.answer()
    
    try:
        # Обновляем меню с новым выбором дней
        text = get_subscription_menu_text(devices=callback_data.devices, days=callback_data.days)
        keyboard = build_subscription_menu(devices=callback_data.devices, days=callback_data.days)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception:
        logger.exception(f'Ошибка выбора дней tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(SubscriptionCallback.filter(F.action == 'select_devices'))
async def select_devices(callback: CallbackQuery, callback_data: SubscriptionCallback):
    """Обрабатывает выбор количества устройств."""
    await callback.answer()
    
    try:
        # Обновляем меню с новым выбором устройств
        text = get_subscription_menu_text(devices=callback_data.devices, days=callback_data.days)
        keyboard = build_subscription_menu(devices=callback_data.devices, days=callback_data.days)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception:
        logger.exception(f'Ошибка выбора устройств tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(SubscriptionCallback.filter(F.action == 'pay'))
async def proceed_to_payment(callback: CallbackQuery, callback_data: SubscriptionCallback):
    """Переход к оплате (пока заглушка)."""
    await callback.answer(
        f"Оплата {callback_data.devices} устройств на {callback_data.days} дней (в разработке)",
        show_alert=True
    )