from sqladmin import ModelView

from app.db.models import Subscription


class SubscriptionAdmin(ModelView, model=Subscription):
    """Админка подписок."""
    
    column_list = [
        'user.telegram_id',
        'user.username',
        Subscription.status,
        Subscription.expires_at,
        Subscription.hwid_limit,
        Subscription.hwid_count,
    ]
    
    column_searchable_list = [Subscription.status]
    column_sortable_list = [Subscription.expires_at]
    
    column_formatters = {
        Subscription.expires_at: lambda m, a: m.expires_at.strftime('%d.%m.%Y %H:%M') if m.expires_at else '-',
    }
    
    column_labels = {
        'user.telegram_id': 'Telegram ID',
        'user.username': 'Username',
        Subscription.status: 'Статус',
        Subscription.expires_at: 'Истекает',
        Subscription.hwid_limit: 'Лимит устройств',
        Subscription.hwid_count: 'Активно устройств',
    }
    
    can_create = False
    can_delete = False
    can_edit = True
    
    name = "Подписка"
    name_plural = "Подписки"
    icon = "fa-solid fa-crown"