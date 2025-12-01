from httpx import HTTPStatusError

from app.services.client import PanelClient, PanelError
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository, UserAlreadyExistsError
from app.db.models import User
from app.core.settings import config


class UserSyncResult:
    """Результат синхронизации пользователя."""
    
    def __init__(self, user: User, created: bool = False, synced: bool = False):
        self.user = user
        self.created = created
        self.synced = synced


class UserService:
    """Управление пользователями."""
    
    def __init__(self):
        self.client = PanelClient()
        
    async def list_users(self, size: int = 50, start: int = 0) -> dict:
        """Возвращает список пользователей из панели."""
        params = {'size': size, 'start': start}
        return await self.client.request('GET', '/api/users', params=params)

    async def get_or_create_user(
        self,
        username: str,
        expire_at: str,
        telegram_id: int,
        description: str,
    ) -> UserSyncResult:
        """
        Создает или синхронизирует пользователя.
        
        Возвращает UserSyncResult с флагами created/synced.
        """
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            db_user = await repo.get_by_telegram_id(telegram_id)
            panel_user = await self._get_panel_user(telegram_id)

            # 1. Юзер и в БД и в панели
            if db_user and panel_user:
                return UserSyncResult(user=db_user)

            # 2. Нет в панели, есть в БД
            if db_user and not panel_user:
                panel_data = await self._create_in_panel(
                    username, expire_at, telegram_id, description
                )
                await session.commit()
                return UserSyncResult(user=db_user, synced=True)

            # 3. Нет в БД, есть в панели
            if panel_user and not db_user:
                user = await repo.create(
                    panel_uuid=panel_user['uuid'],
                    short_uuid=panel_user['shortUuid'],
                    telegram_id=telegram_id,
                    username=panel_user['username'],
                    subscription_url=panel_user['subscriptionUrl'],
                    hwid_limit=panel_user.get('hwidDeviceLimit'),
                )
                await session.commit()
                return UserSyncResult(user=user, synced=True)

            # 4. Юзер новый
            panel_data = await self._create_in_panel(
                username, expire_at, telegram_id, description
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
            return UserSyncResult(user=user, created=True)

    async def _get_panel_user(self, telegram_id: int) -> dict | None:
        """Получает пользователя из панели по telegram_id."""
        try:
            res = await self.client.request(
                'GET',
                f'/api/users/by-telegram-id/{telegram_id}',
            )
            users = res.get('response') or []
            return users[0] if users else None
        except PanelError as e:
            if '404' in str(e):
                return None
            raise

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