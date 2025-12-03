from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.user import UserService
from app.services.balance import BalanceService
from app.services.payment import PaymentService
from app.bot.keyboards.subscription import build_subscription_menu, get_subscription_menu_text, calculate_price
from app.bot.keyboards.payment import build_payment_menu, get_payment_menu_text
from app.bot.keyboards.main_menu import build_main_menu, get_main_menu_text
from app.services.currency import CurrencyService
from app.bot.keyboards.callback_data import MainMenuCallback, SubscriptionCallback, PaymentCallback
from app.bot.states.subscription import SubscriptionStates
from loguru import logger

router = Router()


@router.callback_query(MainMenuCallback.filter(F.action == 'upgrade'))
async def show_subscription_menu(callback: CallbackQuery, callback_data: MainMenuCallback):
    """Открывает меню выбора тарифа."""
    await callback.answer()
    
    try:
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
        price, _ = calculate_price(callback_data.devices, callback_data.days)
        
        balance_service = BalanceService()
        user_balance = await balance_service.get_balance(callback.from_user.id)
        user_balance_float = float(user_balance)
        
        await state.update_data(
            devices=callback_data.devices,
            days=callback_data.days,
            price=price,
            balance=user_balance_float
        )
        await state.set_state(SubscriptionStates.selecting_payment)
        
        text = await get_payment_menu_text(callback_data.devices, callback_data.days, price, user_balance_float)
        keyboard = await build_payment_menu(price, user_balance_float)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        logger.info(f'Переход к оплате для tg_id={callback.from_user.id}')
        
    except Exception:
        logger.exception(f'Ошибка перехода к оплате tg_id={callback.from_user.id}')
        await callback.answer('❌ Произошла ошибка', show_alert=True)


@router.callback_query(PaymentCallback.filter(F.method == 'balance'))
async def pay_with_balance(callback: CallbackQuery, state: FSMContext, callback_data: PaymentCallback):
    """Оплата балансом."""
    telegram_id = callback.from_user.id
    
    try:
        data = await state.get_data()
        amount_rub = callback_data.amount_rub or data['price']
        devices = data['devices']
        days = data['days']
        user_balance = data.get('balance', 0)
        
        if user_balance < amount_rub:
            await callback.answer(
                f"❌ Недостаточно средств на балансе\nНужно: {amount_rub}₽\nЕсть: {user_balance:.2f}₽",
                show_alert=True
            )
            return
        
        payment_service = PaymentService()
        result = await payment_service.process_balance_payment(
            telegram_id=telegram_id,
            amount=amount_rub,
            devices=devices,
            days=days
        )
        
        await state.clear()
        
        user_service = UserService()
        user = await user_service.get_user_by_telegram_id(telegram_id)
        
        text = (
            f"✅ <b>Оплата успешна!</b>\n\n"
            f"Списано: <b>{result['amount']}₽</b>\n"
            f"Новый баланс: <b>{result['new_balance']:.2f}₽</b>\n"
            f"Тариф: <b>{result['devices']} устройств</b> на <b>{result['days']} дней</b>\n\n"
        ) + get_main_menu_text(user)
        
        keyboard = build_main_menu(user)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
        logger.info(
            f'Оплата балансом успешна: tg_id={telegram_id}, '
            f'amount={amount_rub}, devices={devices}, days={days}'
        )
        
    except ValueError as e:
        logger.warning(f'Ошибка оплаты для tg_id={telegram_id}: {e}')
        await callback.answer(f'❌ {e}', show_alert=True)
        
    except Exception:
        logger.exception(f'Неожиданная ошибка оплаты tg_id={telegram_id}')
        await callback.answer('❌ Произошла ошибка при обработке платежа', show_alert=True)


@router.callback_query(PaymentCallback.filter(F.method == 'card'))
async def pay_with_card(callback: CallbackQuery, state: FSMContext, callback_data: PaymentCallback):
    """Оплата картой (заглушка)."""
    data = await state.get_data()
    amount_rub = callback_data.amount_rub or data['price']
    
    await callback.answer(
        f"Оплата картой: {data['devices']} устройств на {data['days']} дней = {amount_rub}₽ (в разработке)",
        show_alert=True
    )


@router.callback_query(PaymentCallback.filter(F.method == 'crypto'))
async def pay_with_crypto(callback: CallbackQuery, state: FSMContext, callback_data: PaymentCallback):
    """Оплата криптой (заглушка)."""
    
    data = await state.get_data()
    amount_rub = callback_data.amount_rub or data['price']
    
    currency_service = CurrencyService()
    amount_usd = await currency_service.convert_rub_to_usd(amount_rub)
    
    await callback.answer(
        f"Оплата криптой: {data['devices']} устройств на {data['days']} дней = ${amount_usd} (в разработке)",
        show_alert=True
    )