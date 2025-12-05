from sqladmin import ModelView

from app.db.models import Wallet


class WalletAdmin(ModelView, model=Wallet):
    """Админка балансов."""
    
    column_list = [
        'user.telegram_id',
        'user.username',
        Wallet.balance,
        Wallet.updated_at,
    ]
    
    column_sortable_list = [Wallet.balance, Wallet.updated_at]
    
    column_formatters = {
        Wallet.balance: lambda m, a: f'{m.balance:.2f} ₽',
        Wallet.updated_at: lambda m, a: m.updated_at.strftime('%d.%m.%Y %H:%M') if m.updated_at else '-',
    }
    
    column_labels = {
        'user.telegram_id': 'Telegram ID',
        'user.username': 'Username',
        Wallet.balance: 'Баланс',
        Wallet.updated_at: 'Обновлён',
    }
    
    can_create = False
    can_delete = False
    can_edit = True
    
    name = "Баланс"
    name_plural = "Балансы"
    icon = "fa-solid fa-wallet"