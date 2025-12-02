from aiogram.filters.callback_data import CallbackData


class MainMenuCallback(CallbackData, prefix="menu"):
    """Колбэки главного меню."""
    action: str  # 'devices', 'subscription', 'connect'


class DeviceCallback(CallbackData, prefix="device"):
    """Колбэки управления устройствами."""
    action: str  # 'list', 'delete', 'reset'
    hwid: str | None = None


class SubscriptionCallback(CallbackData, prefix="sub"):
    """Колбэки подписки."""
    action: str  # 'upgrade', 'buy'
    devices: int | None = None
    months: int | None = None