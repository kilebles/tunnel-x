from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import PaymentCallback, MainMenuCallback


def build_payment_menu() -> InlineKeyboardMarkup:
    """
    Строит меню выбора способа оплаты.
    """
    
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="💳 Карта (₽)",
        callback_data=PaymentCallback(method='card').pack()
    )
    
    builder.button(
        text="💸 Криптокошелёк ($)",
        callback_data=PaymentCallback(method='crypto').pack()
    )
    
    builder.button(
        text="◀️ Назад",
        callback_data=MainMenuCallback(action='back').pack()
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_payment_menu_text(devices: int, days: int, price: int) -> str:
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
    
    text = f"Тариф: <b>{devices} устройств</b> на <b>{period}</b>\n"
    text += f"К оплате: <b>{price}₽</b>\n\n"
    text += f"<blockquote><i>Выберите удобный способ оплаты</i></blockquote>"
    
    return text