from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.user import User
from app.bot.keyboards.callback_data import MainMenuCallback


def build_main_menu(user: User) -> InlineKeyboardMarkup:
    """Строит главное меню с динамическими кнопками."""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔗 Подключиться",
        web_app=WebAppInfo(url=user.subscription_url)
    )
    
    if user.subscription.hwid_count > 0:
        builder.button(
            text=f"📱 Устройства ({user.subscription.hwid_count}/{user.subscription.hwid_limit or '∞'})",
            callback_data=MainMenuCallback(action='devices').pack()
        )
    
    status = user.subscription.status
    
    if status == 'FREE':
        builder.button(
            text="💎 Перейти на премиум",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    elif status == 'TRIAL':
        builder.button(
            text="🌏 Остаться на премиум",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    elif status == 'PREMIUM':
        builder.button(
            text="🔄 Продлить тариф",
            callback_data=MainMenuCallback(action='upgrade').pack()
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_text(user: User) -> str:
    """Генерирует текст для главного меню."""
    from datetime import datetime, timezone
    
    status = user.subscription.status
    expires = user.subscription.expires_at
    username = user.username or f"user_{user.telegram_id}"
    balance = float(user.wallet.balance)
    
    # Заголовок
    text = f"<b>@{username}</b>\n"
    text += f"<code>ID: {user.telegram_id}</code>\n\n"
    
    # Статус
    status_emoji = {
        'FREE': '🆓',
        'TRIAL': '⏳',
        'PREMIUM': '💎'
    }
    
    status_name = {
        'FREE': 'Бесплатный',
        'TRIAL': 'Премиум',
        'PREMIUM': 'Премиум'
    }
    
    text += f"{status_emoji.get(status, '📱')} Тариф: <b>{status_name.get(status, status)}</b>\n"
    
    # Баланс
    text += f"💰 Баланс: <b>{balance:.2f}₽</b>\n"
    
    # Время подписки (только для TRIAL и PREMIUM)
    if status in ('TRIAL', 'PREMIUM') and expires:
        time_left = expires - datetime.now(timezone.utc)
        days = time_left.days
        hours = time_left.seconds // 3600
        
        if days > 0:
            text += f"⏰ Осталось: <b>{days} дн. {hours} ч.</b>\n"
        elif hours > 0:
            text += f"⏰ Осталось: <b>{hours} ч.</b>\n"
        else:
            minutes = (time_left.seconds % 3600) // 60
            text += f"⏰ Осталось: <b>{minutes} мин.</b>\n"
    
    text += "\n"
    
    if status == 'FREE':
        text += "<blockquote><i>Бесплатный тариф имеет ограниченную скорость, количество устройств и доступен только один сервер </i></blockquote>"
    elif status == 'TRIAL':
        text += "<blockquote><i>Оставайтесь на премиум тарифе, чтобы скорость и трафик были не ограничены, а доступных локаций было множество </i></blockquote>"
    elif status == 'PREMIUM':
        text += "<blockquote><i>Вы под защитой, спасибо что выбираете нас </i></blockquote>"
    
    return text