from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import SubscriptionCallback, MainMenuCallback


def calculate_price(devices: int, days: int) -> tuple[int, int]:
    """
    Расчёт цены за подписку.
    Возвращает (итоговая_цена, полная_цена_без_скидки).
    """
    base_monthly = {
        1: 150,
        2: 200,
        4: 270,
        10: 400
    }
    
    monthly = base_monthly.get(devices, 200)
    months = days / 30
    full_price = int(monthly * months)
    
    # Скидки за срок
    discount = 1.0
    if days >= 90:
        discount = 0.9   # -10%
    if days >= 180:
        discount = 0.83  # -17%
    if days >= 360:
        discount = 0.75  # -25%
    
    final_price = int(monthly * months * discount)
    
    return final_price, full_price


def build_subscription_menu(devices: int = 2, days: int = 30) -> InlineKeyboardMarkup:
    """Строит меню выбора тарифа с динамическими галочками."""
    builder = InlineKeyboardBuilder()
    
    price, full_price = calculate_price(devices, days)
    
    # Кнопка оплаты со скидкой если есть
    if price < full_price:
        discount_percent = int((1 - price / full_price) * 100)
        button_text = f"💳 Оплатить {price}₽ 🔥 -{discount_percent}%"
    else:
        button_text = f"💳 Оплатить {price}₽"
    
    builder.button(
        text=button_text,
        callback_data=SubscriptionCallback(action='pay', devices=devices, days=days).pack()
    )
    
    days_options = [30, 90, 180, 360]
    devices_options = [1, 2, 4, 10]
    
    for day, dev in zip(days_options, devices_options):
        day_checkmark = "🫆 " if day == days else ""
        builder.button(
            text=f"{day_checkmark}{day} дней",
            callback_data=SubscriptionCallback(action='select_days', devices=devices, days=day).pack()
        )
        
        dev_checkmark = "🫆 " if dev == devices else ""
        builder.button(
            text=f"{dev_checkmark}{dev} устройств",
            callback_data=SubscriptionCallback(action='select_devices', devices=dev, days=days).pack()
        )
    
    builder.button(
        text="◀️ Назад",
        callback_data=MainMenuCallback(action='back').pack()
    )
    
    builder.adjust(1, 2, 2, 2, 2, 1)
    
    return builder.as_markup()


def get_subscription_menu_text(devices: int, days: int) -> str:
    """Генерирует текст для меню подписки."""
    price, full_price = calculate_price(devices, days)
    
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
    
    text = f"Выбрано: <b>{devices} устройств</b> на <b>{period}</b>\n"
    
    # Показываем скидку в тексте если есть
    if price < full_price:
        text += f"Цена: <s>{full_price}₽</s> <b>{price}₽</b>\n\n"
    else:
        text += f"Цена: <b>{price}₽</b>\n\n"
    
    text += f"<blockquote><i>Чем длиннее период – тем больше выгода. Количество выбранных устройств определяет, сколько можно подключить одновременно</i></blockquote>"
    
    return text