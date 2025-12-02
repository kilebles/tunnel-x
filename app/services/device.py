from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.services.client import PanelClient


class DeviceService:
    """Управление устройствами пользователей."""
    
    def __init__(self):
        self.client = PanelClient()
    
    async def get_devices(self, telegram_id: int) -> tuple[list[dict], int]:
        """Получает список устройств и лимит пользователя."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                return [], 0
            
            data = await self.client.request('GET', f'/api/hwid/devices/{user.panel_uuid}')
            response = data.get('response', {})
            devices = response.get('devices', [])
            
            await session.refresh(user, ['subscription'])
            user.subscription.hwid_count = len(devices)
            await session.commit()
            
            return devices, user.subscription.hwid_limit or 0
    
    async def delete_device(self, telegram_id: int, hwid: str) -> tuple[int, int]:
        """Удаляет устройство, возвращает (оставшееся кол-во, лимит)."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            payload = {'userUuid': user.panel_uuid, 'hwid': hwid}
            await self.client.request('POST', '/api/hwid/devices/delete', json=payload)
            
            devices, limit = await self.get_devices(telegram_id)
            return len(devices), limit
    
    async def reset_devices(self, telegram_id: int) -> None:
        """Удаляет все устройства пользователя."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            data = await self.client.request('GET', f'/api/hwid/devices/{user.panel_uuid}')
            response = data.get('response', {})
            devices = response.get('devices', [])
            
            for device in devices:
                payload = {'userUuid': user.panel_uuid, 'hwid': device['hwid']}
                await self.client.request('POST', '/api/hwid/devices/delete', json=payload)
            
            await session.refresh(user, ['subscription'])
            user.subscription.hwid_count = 0
            await session.commit()