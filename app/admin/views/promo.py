from sqladmin import ModelView

from app.db.models import PromoCode


class PromoCodeAdmin(ModelView, model=PromoCode):
    """Админка промокодов."""
    
    column_list = [
        PromoCode.code,
        PromoCode.percentage,
        PromoCode.used_count,
        PromoCode.max_uses,
        PromoCode.is_active,
        PromoCode.expires_at,
        PromoCode.created_at,
    ]
    
    column_searchable_list = [PromoCode.code]
    column_sortable_list = [PromoCode.created_at, PromoCode.percentage, PromoCode.used_count]
    column_default_sort = [(PromoCode.created_at, True)]
    
    column_formatters = {
        PromoCode.percentage: lambda m, a: f'{m.percentage}%',
        PromoCode.max_uses: lambda m, a: str(m.max_uses) if m.max_uses else '∞',
        PromoCode.used_count: lambda m, a: f'{m.used_count}/{m.max_uses or "∞"}',
        PromoCode.expires_at: lambda m, a: m.expires_at.strftime('%d.%m.%Y %H:%M') if m.expires_at else 'Не ограничен',
        PromoCode.created_at: lambda m, a: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
    }
    
    column_labels = {
        PromoCode.code: 'Промокод',
        PromoCode.percentage: 'Скидка',
        PromoCode.max_uses: 'Макс. использований',
        PromoCode.used_count: 'Использовано',
        PromoCode.is_active: 'Активен',
        PromoCode.expires_at: 'Истекает',
        PromoCode.created_at: 'Создан',
    }
    
    form_excluded_columns = ['created_at', 'used_count']
    
    can_create = True
    can_delete = True
    can_edit = True
    
    name = "Промокод"
    name_plural = "Промокоды"
    icon = "fa-solid fa-ticket"