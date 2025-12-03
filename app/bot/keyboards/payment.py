from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import PaymentCallback, MainMenuCallback
from app.services.currency import CurrencyService


async def build_payment_menu(price_rub: int, user_balance: float) -> InlineKeyboardMarkup:
    """Строит меню выбора способа оплаты."""
    builder = InlineKeyboardBuilder()
    
    # Получаем актуальный курс
    currency_service = CurrencyService()
    price_usd = await currency_service.convert_rub_to_usd(price_rub)
    
    # Кнопка "Баланс" если хватает средств
    if user_balance >= price_rub:
        builder.button(
            text=f"💰 Баланс ({price_rub}₽)",
            callback_data=PaymentCallback(method='balance', amount_rub=price_rub).pack()
        )
    
    builder.button(
        text=f"💳 Карта ({price_rub}₽)",
        callback_data=PaymentCallback(method='card', amount_rub=price_rub).pack()
    )
    
    builder.button(
        text=f"💸 Криптокошелёк (${price_usd})",
        callback_data=PaymentCallback(method='crypto', amount_rub=price_rub).pack()
    )
    
    builder.button(
        text="◀️ Назад",
        callback_data=MainMenuCallback(action='back').pack()
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


async def get_payment_menu_text(devices: int, days: int, price: int, user_balance: float) -> str:
    """Генерирует текст для меню оплаты."""
    if days == 30:
        period = "1 месяц"
    elif days == 90:
        period = "3 месяца"
    elif days == 180:
        period = "6 месяцев"
    elif days == 360:
        period = "1 год"
    else:
        period = f"{days} дней"
    
    # Получаем актуальный курс
    currency_service = CurrencyService()
    price_usd = await currency_service.convert_rub_to_usd(price)
    
    text = f"<b>💳 Выбери способ оплаты</b>\n\n"
    text += f"Тариф: <b>{devices} устройств</b> на <b>{period}</b>\n"
    text += f"К оплате: <b>{price}₽</b> ≈${price_usd}\n"
    
    # Показываем баланс если есть
    if user_balance > 0:
        text += f"Твой баланс: <b>{user_balance:.2f}₽</b>\n"
    
    text += "\n"
    text += f"<blockquote><i>Выбери удобный способ оплаты</i></blockquote>"
    
    return text