from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.user import User
from app.bot.keyboards.callback_data import MainMenuCallback


def build_main_menu(user: User) -> InlineKeyboardMarkup:
    """
    Строит главное меню с динамическими кнопками.
    
    Кнопки:
    - Подключиться (URL на subscription_url)
    - Устройства (если hwid_count > 0)
    - Продлить/Перейти на премиум (колбэк, зависит от статуса)
    """
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопка "Подключиться" (URL из БД)
    builder.button(
        text="🔗 Подключиться",
        url=user.subscription_url
    )
    
    # 2. Кнопка "Устройства" (только если есть устройства)
    if user.subscription.hwid_count > 0:
        builder.button(
            text=f"📱 Устройства ({user.subscription.hwid_count}/{user.subscription.hwid_limit or '∞'})",
            callback_data=MainMenuCallback(action='devices').pack()
        )
    
    # 3. Кнопка подписки (колбэк для открытия меню тарифов)
    status = user.subscription.status
    
    if status == 'FREE':
        builder.button(
            text="💎 Перейти на премиум",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    elif status == 'TRIAL':
        builder.button(
            text="🎁 Купить премиум со скидкой",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    elif status == 'PREMIUM':
        builder.button(
            text="🔄 Продлить подписку",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_text(user: User) -> str:
    """Генерирует текст для главного меню."""
    status = user.subscription.status
    expires = user.subscription.expires_at
    
    status_emoji = {
        'FREE': '🆓',
        'TRIAL': '⏳',
        'PREMIUM': '💎'
    }
    
    status_name = {
        'FREE': 'Бесплатный',
        'TRIAL': 'Пробный премиум',
        'PREMIUM': 'Премиум'
    }
    
    text = f"<b>Главное меню</b>\n\n"
    text += f"{status_emoji.get(status, '📱')} Статус: <b>{status_name.get(status, status)}</b>\n"
    
    if expires:
        from datetime import datetime, timezone
        days_left = (expires - datetime.now(timezone.utc)).days
        
        if days_left > 0:
            text += f"⏰ Осталось: <b>{days_left} дн.</b>\n"
        elif status != 'FREE':
            text += f"⚠️ Подписка истекла\n"
    
    text += f"📱 Устройств: <b>{user.subscription.hwid_count}/{user.subscription.hwid_limit or '∞'}</b>\n"
    
    return text