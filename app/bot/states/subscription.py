from aiogram.fsm.state import State, StatesGroup


class SubscriptionStates(StatesGroup):
    """Состояния для покупки подписки."""
    selecting_payment = State()  # Выбор способа оплаты
    processing = State()  # Ожидание оплаты