from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import PaymentCallback, MainMenuCallback


def convert_rub_to_usd(rub: int) -> float:
    """Конвертирует рубли в доллары по текущему курсу."""
    # TODO: Можно добавить API для получения актуального курса
    # Пока используем примерный курс 1 USD = 95 RUB
    USD_RATE = 95
    return round(rub / USD_RATE, 2)


def build_payment_menu(price_rub: int) -> InlineKeyboardMarkup:
    """Строит меню выбора способа оплаты."""
    builder = InlineKeyboardBuilder()
    
    price_usd = convert_rub_to_usd(price_rub)
    
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
    
    price_usd = convert_rub_to_usd(price)
    
    text = f"Тариф: <b>{devices} устройств</b> на <b>{period}</b>\n"
    text += f"К оплате: <b>{price}₽</b> ≈${price_usd}\n\n"
    text += f"<blockquote><i>Выберите удобный способ оплаты</i></blockquote>"
    
    return text