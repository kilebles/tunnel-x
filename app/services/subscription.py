from datetime import datetime, timezone, timedelta

from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.services.client import PanelClient
from app.core.settings import config
from loguru import logger


class SubscriptionService:
    """Управление подписками пользователей."""
    
    def __init__(self):
        self.client = PanelClient()
    
    async def expire_subscription(self, telegram_id: int) -> None:
        """Переводит пользователя на FREE после истечения подписки."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                logger.warning(f'Пользователь tg_id={telegram_id} не найден при истечении')
                return
            
            await session.refresh(user, ['subscription'])
            
            user.subscription.status = 'FREE'
            user.subscription.expires_at = datetime.now(timezone.utc)
            
            free_expires = datetime.now(timezone.utc) + timedelta(days=365)
            
            await self._update_user_in_panel(
                user_uuid=user.panel_uuid,
                internal_squads=[config.INTERNAL_SQUAD_FREE],
                external_squad=config.EXTERNAL_SQUAD_FREE,
                expire_at=free_expires.isoformat(),
                hwid_limit=1,
            )
            
            await session.commit()
            logger.info(f'Пользователь tg_id={telegram_id} переведён на FREE')
    
    async def activate_premium(
        self,
        telegram_id: int,
        duration_days: int,
        hwid_limit: int
    ) -> None:
        """Активирует премиум подписку."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                logger.warning(f'Пользователь tg_id={telegram_id} не найден')
                return
            
            await session.refresh(user, ['subscription'])
            
            expires = datetime.now(timezone.utc) + timedelta(days=duration_days)
            
            user.subscription.status = 'PREMIUM'
            user.subscription.expires_at = expires
            user.subscription.hwid_limit = hwid_limit
            
            await self._update_user_in_panel(
                user_uuid=user.panel_uuid,
                internal_squads=[config.INTERNAL_SQUAD_MAIN],
                external_squad=config.EXTERNAL_SQUAD_PREMIUM,
                expire_at=expires.isoformat(),
                hwid_limit=hwid_limit,
            )
            
            await session.commit()
            logger.info(f'Активирован PREMIUM для tg_id={telegram_id} на {duration_days} дней')
    
    async def _update_user_in_panel(
        self,
        user_uuid: str,
        internal_squads: list[str],
        external_squad: str,
        expire_at: str,
        hwid_limit: int,
    ) -> None:
        """Обновляет пользователя в панели."""
        payload = {
            'uuid': user_uuid,
            'activeInternalSquads': internal_squads,
            'externalSquadUuid': external_squad,
            'expireAt': expire_at,
            'hwidDeviceLimit': hwid_limit,
        }
        
        await self.client.request('PATCH', '/api/users', json=payload)