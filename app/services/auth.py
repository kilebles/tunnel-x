"""
Авторизация в панели и управление JWT токеном.
"""

import logging
from httpx import AsyncClient

from app.core.settings import config

logger = logging.getLogger(__name__)


class PanelAuth:
    def __init__(self):
        self.url = f'{config.PANEL_URL}/api/auth/login'
        self.username = config.PANEL_LOGIN
        self.password = config.PANEL_PASSWORD
        self.token = None
        
    async def login(self) -> str:
        async with AsyncClient() as client:
            response = await client.post(self.url, json={
                'username': self.username,
                'password': self.password,
            })
            logger.info('status %s', response.status_code)
            logger.info('auth response %s', response.text)
            
            data = response.json()
            self.token = data['response']['accessToken']
            return self.token