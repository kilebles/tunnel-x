from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.subscription import build_subscription_menu, get_subscription_menu_text, calculate_price
from app.bot.keyboards.payment import build_payment_menu, get_payment_menu_text
from app.bot.keyboards.callback_data import MainMenuCallback, SubscriptionCallback, PaymentCallback
from app.bot.states.subscription import SubscriptionStates
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
        text = get_subscription_menu_text(devices=callback_data.devices, days=callback_data.days)
        keyboard = build_subscription_menu(devices=callback_data.devices, days=callback_data.days)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception:
        logger.exception(f'Ошибка выбора устройств tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(SubscriptionCallback.filter(F.action == 'pay'))
async def proceed_to_payment(
    callback: CallbackQuery, 
    callback_data: SubscriptionCallback,
    state: FSMContext
):
    """Переход к выбору способа оплаты."""
    await callback.answer()
    
    try:
        # Сохраняем выбор в FSM
        price, _ = calculate_price(callback_data.devices, callback_data.days)
        
        await state.update_data(
            devices=callback_data.devices,
            days=callback_data.days,
            price=price
        )
        await state.set_state(SubscriptionStates.selecting_payment)
        
        text = get_payment_menu_text(callback_data.devices, callback_data.days, price)
        keyboard = build_payment_menu()
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        logger.info(f'Переход к оплате для tg_id={callback.from_user.id}')
        
    except Exception:
        logger.exception(f'Ошибка перехода к оплате tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(PaymentCallback.filter(F.method == 'card'))
async def pay_with_card(callback: CallbackQuery, state: FSMContext):
    """Оплата картой (заглушка)."""
    data = await state.get_data()
    
    await callback.answer(
        f"Оплата картой: {data['devices']} устройств на {data['days']} дней = {data['price']}₽ (в разработке)",
        show_alert=True
    )


@router.callback_query(PaymentCallback.filter(F.method == 'crypto'))
async def pay_with_crypto(callback: CallbackQuery, state: FSMContext):
    """Оплата криптой (заглушка)."""
    data = await state.get_data()
    
    await callback.answer(
        f"Оплата криптой: {data['devices']} устройств на {data['days']} дней = {data['price']}₽ (в разработке)",
        show_alert=True
    )