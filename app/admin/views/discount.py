from sqladmin import ModelView

from app.db.models import Discount


class DiscountAdmin(ModelView, model=Discount):
    """Админка глобальных скидок."""
    
    column_list = [
        Discount.name,
        Discount.percentage,
        Discount.is_active,
        Discount.created_at,
    ]
    
    column_searchable_list = [Discount.name]
    column_sortable_list = [Discount.created_at, Discount.percentage]
    column_default_sort = [(Discount.created_at, True)]
    
    column_formatters = {
        Discount.percentage: lambda m, a: f'{m.percentage}%',
        Discount.created_at: lambda m, a: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
        Discount.updated_at: lambda m, a: m.updated_at.strftime('%d.%m.%Y %H:%M') if m.updated_at else '-',
    }
    
    column_labels = {
        Discount.name: 'Название',
        Discount.percentage: 'Скидка',
        Discount.is_active: 'Активна',
        Discount.created_at: 'Создана',
        Discount.updated_at: 'Обновлена',
    }
    
    form_excluded_columns = ['created_at', 'updated_at']
    
    can_create = True
    can_delete = True
    can_edit = True
    
    name = "Скидка"
    name_plural = "Глобальные скидки"
    icon = "fa-solid fa-percent"