from httpx import HTTPStatusError

from app.services.client import PanelClient
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.core.logger import logger


class UserService:
    def __init__(self):
        self.client = PanelClient()
        self.default_squad = '0b93d216-44d4-41ee-9a90-831bd6c02f9a'
        
    async def list_users(self, size: int = 50, start: int = 0):
        """
        Возвращает список пользователей из панели.
        """
        
        params = {'size': size, 'start': start}

        try:
            return await self.client.request(
                'GET',
                '/api/users',
                params=params,
            )
        except HTTPStatusError as exc:
            logger.error(
                'Ошибка панели при list_users статус=%s',
                exc.response.status_code,
            )
            return {'error': True}

    async def _get_panel_user(self, telegram_id):
        """
        Возвращает пользователя из панели по telegram_id.
        """
        
        try:
            res = await self.client.request(
                'GET',
                f'/api/users/by-telegram-id/{telegram_id}',
            )
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

        users = res.get('response') or []
        return users[0] if users else None

    async def _sync_existing(self, session, repo, panel_user, existing, telegram_id):
        """
        Синхронизирует пользователя в панели и БД.
        """
        
        if panel_user and existing:
            return {'exists': True, 'user': existing}

        if panel_user and not existing:
            user = await repo.create(
                panel_uuid=panel_user['uuid'],
                short_uuid=panel_user['shortUuid'],
                telegram_id=telegram_id,
                username=panel_user['username'],
                subscription_url=panel_user['subscriptionUrl'],
                hwid_limit=panel_user.get('hwidDeviceLimit'),
            )
            logger.info(
                'Синхронизирован пользователь tg_id=%s id=%s',
                telegram_id,
                user.id,
            )
            return {'exists': True, 'user': user}

        if existing and not panel_user:
            await repo.delete(existing)
            await session.commit()
            logger.info(
                'Удалена устаревшая запись tg_id=%s',
                telegram_id,
            )

        return {'exists': False}

    async def _create_panel_user(self, username, expire_at, telegram_id, description):
        """
        Создает пользователя в панели.
        """
        
        payload = {
            'username': username,
            'expireAt': expire_at,
            'telegramId': telegram_id,
            'activeInternalSquads': [self.default_squad],
            'description': description,
        }

        try:
            return await self.client.request(
                'POST',
                '/api/users',
                json=payload,
            )
        except HTTPStatusError as exc:
            logger.error(
                'Ошибка панели при создании tg_id=%s статус=%s',
                telegram_id,
                exc.response.status_code,
            )
            return {'error': True}

    async def _create_db_user(self, repo, panel_data, telegram_id, username):
        """
        Создает пользователя в БД.
        """
        user = await repo.create(
            panel_uuid=panel_data['uuid'],
            short_uuid=panel_data['shortUuid'],
            telegram_id=telegram_id,
            username=username,
            subscription_url=panel_data['subscriptionUrl'],
            hwid_limit=panel_data.get('hwidDeviceLimit'),
        )
        return user

    async def create_user(self, username, expire_at, telegram_id, description):
        """
        Основной метод: создает пользователя при необходимости.
        """
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            panel_user = await self._get_panel_user(telegram_id)
            existing = await repo.get_by_telegram_id(telegram_id)

            sync = await self._sync_existing(session, repo, panel_user, existing, telegram_id)
            if sync['exists']:
                return {'error': True}

            panel_resp = await self._create_panel_user(
                username,
                expire_at,
                telegram_id,
                description,
            )

            if not panel_resp or panel_resp.get('error'):
                return {'error': True}

            data = panel_resp['response']

            user = await self._create_db_user(
                repo,
                data,
                telegram_id,
                username,
            )

            logger.info(
                'Создан пользователь tg_id=%s id=%s',
                telegram_id,
                user.id,
            )

            return user