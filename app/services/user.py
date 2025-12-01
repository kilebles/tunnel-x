from datetime import datetime, timezone, timedelta

from app.services.client import PanelClient, PanelError
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository, UserAlreadyExistsError
from app.db.models.user import User
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
        telegram_id: int,
        description: str,
    ) -> UserSyncResult:
        """
        Создает или синхронизирует пользователя с триалом.
        """
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            db_user = await repo.get_by_telegram_id(telegram_id)
            panel_user = await self._get_panel_user(telegram_id)

            # 4. Оба существуют
            if db_user and panel_user:
                return UserSyncResult(user=db_user)

            # 2. Нет в панели, есть в БД - создаём в панели
            if db_user and not panel_user:
                trial_expires = datetime.now(timezone.utc) + timedelta(days=config.TRIAL_DAYS)
                
                panel_data = await self._create_in_panel(
                    username=username,
                    telegram_id=telegram_id,
                    description=description,
                    expire_at=trial_expires.isoformat(),
                    internal_squads=[config.INTERNAL_SQUAD_MAIN],
                    external_squad=config.EXTERNAL_SQUAD_PREMIUM,
                )
                
                await session.commit()
                return UserSyncResult(user=db_user, synced=True)

            # 3. Нет в БД, есть в панели - создаём в БД
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

            # 1. Оба не существуют - создаём с триалом
            trial_expires = datetime.now(timezone.utc) + timedelta(days=config.TRIAL_DAYS)
            
            panel_data = await self._create_in_panel(
                username=username,
                telegram_id=telegram_id,
                description=description,
                expire_at=trial_expires.isoformat(),
                internal_squads=[config.INTERNAL_SQUAD_MAIN],
                external_squad=config.EXTERNAL_SQUAD_PREMIUM,
            )
            
            user = await repo.create(
                panel_uuid=panel_data['uuid'],
                short_uuid=panel_data['shortUuid'],
                telegram_id=telegram_id,
                username=username,
                subscription_url=panel_data['subscriptionUrl'],
                hwid_limit=panel_data.get('hwidDeviceLimit'),
            )
            
            # Загружаем связанные объекты
            await session.refresh(user, ['subscription', 'wallet'])
            
            # Устанавливаем триал
            user.subscription.status = 'TRIAL'
            user.subscription.trial_used = True
            user.subscription.trial_started_at = datetime.now(timezone.utc)
            user.subscription.trial_expires_at = trial_expires
            user.subscription.expires_at = trial_expires
            
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
        telegram_id: int,
        description: str,
        expire_at: str,
        internal_squads: list[str],
        external_squad: str,
    ) -> dict:
        """Создает пользователя в панели."""
        payload = {
            'username': username,
            'expireAt': expire_at,
            'telegramId': telegram_id,
            'activeInternalSquads': internal_squads,
            'externalSquadUuid': external_squad,
            'description': description,
        }

        data = await self.client.request('POST', '/api/users', json=payload)
        return data['response']