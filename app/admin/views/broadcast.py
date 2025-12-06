from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import RedirectResponse
import asyncio

from app.db.models import Broadcast
from app.services.broadcast import BroadcastService
from app.bot.dispatcher import bot
from loguru import logger


class BroadcastAdmin(ModelView, model=Broadcast):
    """Админка рассылок."""
    
    column_list = [
        Broadcast.id,
        Broadcast.text,
        Broadcast.status,
        Broadcast.sent_count,
        Broadcast.failed_count,
        Broadcast.created_at,
    ]
    
    column_details_list = [
        Broadcast.id,
        Broadcast.text,
        Broadcast.add_community_button,
        Broadcast.community_button_text,
        Broadcast.community_url,
        Broadcast.add_try_button,
        Broadcast.try_button_text,
        Broadcast.status,
        Broadcast.sent_count,
        Broadcast.failed_count,
        Broadcast.created_at,
        Broadcast.completed_at,
    ]
    
    column_searchable_list = [Broadcast.status]
    column_sortable_list = [Broadcast.created_at, Broadcast.sent_count]
    column_default_sort = [(Broadcast.created_at, True)]
    
    column_formatters = {
        Broadcast.text: lambda m, a: m.text[:50] + '...' if len(m.text) > 50 else m.text,
        Broadcast.status: lambda m, a: {
            'pending': '⏳ Ожидает',
            'sending': '📤 Отправляется',
            'completed': '✅ Завершена',
            'failed': '❌ Ошибка'
        }.get(m.status, m.status),
        Broadcast.add_community_button: lambda m, a: '✅' if m.add_community_button else '❌',
        Broadcast.add_try_button: lambda m, a: '✅' if m.add_try_button else '❌',
        Broadcast.created_at: lambda m, a: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
        Broadcast.completed_at: lambda m, a: m.completed_at.strftime('%d.%m.%Y %H:%M') if m.completed_at else '-',
        Broadcast.sent_count: lambda m, a: f'{m.sent_count} ✅',
        Broadcast.failed_count: lambda m, a: f'{m.failed_count} ❌',
    }
    
    column_labels = {
        Broadcast.id: 'ID',
        Broadcast.text: 'Текст',
        Broadcast.add_community_button: 'Добавить кнопку сообщества',
        Broadcast.community_button_text: 'Текст кнопки сообщества',
        Broadcast.community_url: 'Ссылка на сообщество',
        Broadcast.add_try_button: 'Добавить кнопку "Попробовать"',
        Broadcast.try_button_text: 'Текст кнопки "Попробовать"',
        Broadcast.status: 'Статус',
        Broadcast.sent_count: 'Отправлено',
        Broadcast.failed_count: 'Ошибок',
        Broadcast.created_at: 'Создана',
        Broadcast.completed_at: 'Завершена',
    }
    
    form_columns = [
        Broadcast.text,
        Broadcast.add_community_button,
        Broadcast.community_button_text,
        Broadcast.community_url,
        Broadcast.add_try_button,
        Broadcast.try_button_text,
    ]
    
    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True
    
    name = "Рассылка"
    name_plural = "Рассылки"
    icon = "fa-solid fa-bullhorn"
    
    @action(
        name="send",
        label="📤 Отправить",
        confirmation_message="Запустить рассылку всем пользователям?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def send_broadcast_action(self, request: Request):
        """Запускает рассылку."""
        pks = request.query_params.get("pks", "").split(",")
        
        if not pks or not pks[0]:
            return RedirectResponse(url=request.url_for("admin:list", identity=self.identity), status_code=302)
        
        broadcast_id = int(pks[0])
        
        try:
            service = BroadcastService()
            
            # Запускаем рассылку в фоне
            asyncio.create_task(service.start_broadcast(broadcast_id, bot))
            
            logger.info(f'Запущена рассылка #{broadcast_id}')
            
        except Exception as e:
            logger.exception(f'Ошибка запуска рассылки #{broadcast_id}: {e}')
        
        return RedirectResponse(url=request.url_for("admin:list", identity=self.identity), status_code=302)