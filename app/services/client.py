"""
Клиент панели: авторизация и реквесты.
"""

import logging

from httpx import AsyncClient, HTTPStatusError
from app.services.auth import PanelAuth
from app.core.settings import config

logger = logging.getLogger(__name__)


class PanelClient:
    def __init__(self, auth: PanelAuth | None = None):
        self.base_url = config.PANEL_URL.rstrip('/')
        self.auth = PanelAuth()
    
    async def request(self, method: str, path: str, **kwargs):
        token = await self.auth.get_token()
            
        headers = kwargs.pop('headers',{}) or {}
        if config.PANEL_TOKEN:
            headers["Authorization"] = f"Bearer {config.PANEL_TOKEN}"
        else:
            token = await self.auth.get_token()
            headers['Authorization']= f'Bearer {token}'
        
        url = f'{self.base_url}{path}'
        
        async with AsyncClient() as client:
            try:
                
                response = await client.request(
                    method, 
                    url, 
                    headers=headers,
                    timeout=10, 
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as exc:
                if exc.response.status_code == 401 and not config.PANEL_TOKEN:
                    logger.info('Токен стух, выполняется повторный логин')
                new_token = await self.auth.login()
                headers['Authorization'] = f'Bearer {new_token}'
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    timeout=10,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            raise
        
        