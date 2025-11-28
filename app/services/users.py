from httpx import HTTPStatusError
from app.services.client import PanelClient


class UsersService:
    def __init__(self):
        self.client = PanelClient()
        self.default_squad = '0b93d216-44d4-41ee-9a90-831bd6c02f9a'
        
    async def list_users(self, size: int =  50, start: int= 0):
        params = {'size': size, 'start': start}
        return await self.client.request('GET','/api/users', params=params)

    async def create_user(self, username: str, expire_at: str):
        payload = {
            'username': username,
            'expireAt': expire_at,
            'activeInternalSquads': [self.default_squad]
        }

        try:
            return await self.client.request('POST', '/api/users', json=payload)

        except HTTPStatusError as exc:
            return {
                'error': True,
                'status_code': exc.response.status_code,
                'message': exc.response.json().get('message', 'Ошибка API')
            }