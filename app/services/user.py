from httpx import HTTPStatusError

from app.services.client import PanelClient, PanelError
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository, UserAlreadyExistsError
from app.db.models import User
from app.core.settings import config


class UserService:
    """Управление пользователями."""
    
    def __init__(self):
        self.client = PanelClient()
        
    async def list_users(self, size: int = 50, start: int = 0) -> dict:
        """Возвращает список пользователей из панели."""
        params = {'size': size, 'start': start}
        return await self.client.request('GET', '/api/users', params=params)

    async def create_user(
        self,
        username: str,
        expire_at: str,
        telegram_id: int,
        description: str,
    ) -> User:
        """Создает пользователя в панели и БД."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            if await repo.get_by_telegram_id(telegram_id):
                raise UserAlreadyExistsError(f'User {telegram_id} exists')

            panel_data = await self._create_in_panel(
                username,
                expire_at,
                telegram_id,
                description,
            )

            user = await repo.create(
                panel_uuid=panel_data['uuid'],
                short_uuid=panel_data['shortUuid'],
                telegram_id=telegram_id,
                username=username,
                subscription_url=panel_data['subscriptionUrl'],
                hwid_limit=panel_data.get('hwidDeviceLimit'),
            )
            
            await session.commit()
            return user

    async def _create_in_panel(
        self,
        username: str,
        expire_at: str,
        telegram_id: int,
        description: str,
    ) -> dict:
        """Создает пользователя в панели."""
        payload = {
            'username': username,
            'expireAt': expire_at,
            'telegramId': telegram_id,
            'activeInternalSquads': [config.DEFAULT_SQUAD_ID],
            'description': description,
        }

        data = await self.client.request('POST', '/api/users', json=payload)
        return data['response']