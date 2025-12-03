from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.callback_data import DeviceCallback, MainMenuCallback


def build_devices_menu(devices: list[dict], hwid_limit: int | None) -> InlineKeyboardMarkup:
    """
    Строит меню управления устройствами.
    
    Каждое устройство = 2 кнопки в ряд:
    """
    builder = InlineKeyboardBuilder()
    

    for device in devices:
        hwid = device.get('hwid', 'unknown')
        platform = device.get('platform', '')
        device_model = device.get('deviceModel', 'Устройство')
        
        emoji = _get_platform_emoji(platform)
        
        builder.button(
            text=f"{emoji} {device_model}",
            callback_data=DeviceCallback(action='info', hwid=hwid).pack()
        )
        
        builder.button(
            text="⛓️‍💥 Отвязать",
            callback_data=DeviceCallback(action='delete', hwid=hwid).pack()
        )
    
    builder.button(
        text="◀️ Назад",
        callback_data=MainMenuCallback(action='back').pack()
    )
    
    if devices:
        builder.adjust(2, 2, 2, 2, 2, 1)  # Пары устройств, потом "Назад"
    else:
        builder.adjust(1)  # Только "Назад"
    
    return builder.as_markup()


def get_devices_menu_text(devices: list[dict], hwid_limit: int | None) -> str:
    """Генерирует текст для меню устройств."""
    count = len(devices)
    limit_str = str(hwid_limit) if hwid_limit else '∞'
    
    text = f"<b>📱 Мои устройства: {count}/{limit_str}</b>\n\n"
    
    if not devices:
        text += "<blockquote><i>Когда нет привязанных устройств, можно <b>подключиться</b> с любого</i></blockquote>"
    else:
        text += "<blockquote><i>Разорванная связь лишит устройство защиты и доступа к любимым сайтам до повторного подключения</i></blockquote>"

    
    return text


def _get_platform_emoji(platform: str | None) -> str:
    """Возвращает эмодзи для платформы."""
    if not platform:
        return '📱'
    
    platform_lower = platform.lower()
    
    emoji_map = {
        'ios': '📱',
        'iphone': '📱',
        'ipad': '📱',
        'android': '🤖',
        'macos': '💻',
        'mac': '💻',
        'windows': '🖥',
        'linux': '🐧',
    }
    
    for key, emoji in emoji_map.items():
        if key in platform_lower:
            return emoji
    
    return '📱'