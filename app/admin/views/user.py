from sqladmin import ModelView

from app.db.models import User


class UserAdmin(ModelView, model=User):
    """Админка пользователей."""
    
    column_list = [
        User.telegram_id,
        User.username,
        User.created_at,
    ]
    
    column_searchable_list = [User.telegram_id, User.username]
    column_sortable_list = [User.telegram_id, User.created_at]
    column_default_sort = [(User.created_at, True)]
    
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
    }
    
    column_labels = {
        User.telegram_id: 'Telegram ID',
        User.username: 'Username',
        User.created_at: 'Дата регистрации',
    }
    
    can_create = False
    can_delete = True
    can_edit = True
    
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"