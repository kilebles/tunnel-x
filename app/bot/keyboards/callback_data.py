from aiogram.filters.callback_data import CallbackData


class MainMenuCallback(CallbackData, prefix="menu"):
    """Колбэки главного меню."""
    action: str  # 'devices', 'upgrade', 'back'


class DeviceCallback(CallbackData, prefix="device"):
    """Колбэки управления устройствами."""
    action: str  # 'info', 'delete'
    hwid: str | None = None


class SubscriptionCallback(CallbackData, prefix="sub"):
    """Колбэки подписки."""
    action: str  # 'select_days', 'select_devices', 'pay', 'back'
    devices: int = 2  # По умолчанию
    days: int = 30  # По умолчанию


class PaymentCallback(CallbackData, prefix="payment"):
    """Колбэки оплаты."""
    method: str  # 'card', 'crypto', 'back'