from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import SubscriptionCallback, MainMenuCallback
from app.db.session import AsyncSessionLocal
from app.services.discount import DiscountService


async def calculate_price(devices: int, days: int) -> tuple[int, int, int]:
    """
    Расчёт цены за подписку с учётом глобальной скидки.
    Возвращает (итоговая_цена, полная_цена_без_скидки, процент_глобальной_скидки).
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
    period_discount = 1.0
    if days >= 90:
        period_discount = 0.9
    if days >= 180:
        period_discount = 0.83
    if days >= 360:
        period_discount = 0.75
    
    price_after_period = int(monthly * months * period_discount)
    
    # Глобальная скидка
    async with AsyncSessionLocal() as session:
        discount_service = DiscountService(session)
        global_discount_percent = await discount_service.get_active_global_discount()
    
    if global_discount_percent > 0:
        global_discount_multiplier = 1 - (global_discount_percent / 100)
        final_price = int(price_after_period * global_discount_multiplier)
    else:
        final_price = price_after_period
    
    return final_price, full_price, global_discount_percent


async def build_subscription_menu(devices: int = 2, days: int = 30) -> InlineKeyboardMarkup:
    """Строит меню выбора тарифа с динамическими галочками."""
    builder = InlineKeyboardBuilder()
    
    price, full_price, global_discount = await calculate_price(devices, days)
    
    # Кнопка оплаты со скидкой
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
        text="↩️ Назад",
        callback_data=MainMenuCallback(action='back').pack()
    )
    
    builder.adjust(1, 2, 2, 2, 2, 1)
    
    return builder.as_markup()


async def get_subscription_menu_text(devices: int, days: int) -> str:
    """Генерирует текст для меню подписки."""
    price, full_price, global_discount = await calculate_price(devices, days)
    
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
    
    if price < full_price:
        text += f"Цена: <s>{full_price}₽</s> <b>{price}₽</b>"
        if global_discount > 0:
            async with AsyncSessionLocal() as session:
                from app.services.discount import DiscountService
                discount_service = DiscountService(session)
                
                from sqlalchemy import select
                from app.db.models import Discount
                result = await session.execute(
                    select(Discount.name)
                    .where(Discount.is_active == True)
                    .order_by(Discount.created_at.desc())
                    .limit(1)
                )
                discount_name = result.scalar_one_or_none()
                
                if discount_name:
                    text += f"<b>{discount_name}</b>"
                else:
                    text += f" скидка {global_discount}%"
        text += "\n\n"
    else:
        text += f"Цена: <b>{price}₽</b>\n\n"
    
    text += f"<blockquote><i>Чем длиннее период – тем больше выгода. Количество выбранных устройств определяет, сколько можно подключить одновременно</i></blockquote>"
    
    return text