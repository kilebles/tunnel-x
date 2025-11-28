"""
Клиент панели: авторизация и реквесты.
"""

from httpx import AsyncClient
from app.services.auth import PanelAuth

class PanelClient:
    def __init__(self):
        self.auth = PanelAuth()
    
    async def request(self, method: str, url: str, **kwargs):
        if not self.auth.token:
            await self.auth.login()
            
        headers = kwargs.pop('headers',{})
        headers['Authorization']= f'Bearer {self.auth.token}'
        
        async with AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response.json()
        