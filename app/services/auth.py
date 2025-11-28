"""
Авторизация в панели и управление JWT токеном.
"""

import logging

from jwt import api_jwt
from httpx import AsyncClient
from redis.asyncio import Redis
from datetime import datetime, timezone, timedelta

from app.core.settings import config

logger = logging.getLogger(__name__)


class PanelAuth:
    def __init__(self, redis: Redis | None = None):
        self.url = f'{config.PANEL_URL}/api/auth/login'
        self.username = config.PANEL_LOGIN
        self.password = config.PANEL_PASSWORD
        self.redis_key = 'panel:access_token'
        self.leeway_minutes = 10
        self.redis = redis or Redis.from_url(
            config.REDIS_URL,
            decode_responses=True,
        )
        self.token: str | None = None
        
    async def get_token(self) -> str:
        if self.token and not self._is_expiring(self.token):
            return self.token
        
        cached = await self.redis.get(self.redis_key)
        if cached and not self._is_expiring(cached):
            self.token = cached
            return cached
        
        return await self.login()
        
    async def login(self) -> str:
        async with AsyncClient() as client:
            response = await client.post(
                self.url, 
                json={
                    'username': self.username, 
                    'password': self.password,
                },
                timeout=10,
            )
            
            response.raise_for_status()
            data = response.json()
            token = data['response']['accessToken']
            
            self.token = token
            ttl = self._calc_ttl(token)
            if ttl >0:
                await self.redis.set(self.redis_key, token, ex=ttl)
                
            logger.info('Токен панели обновлен, ttl %s секунд', ttl)
            return token
        
    def _decode(self, token: str) -> dict:
        return api_jwt.decode_complete(
            jwt=token,
            key=None,
            algorithms=["HS256"],
            options={
                "verify_signature": False,
                "verify_exp": False,
            }
        )["payload"]
        
    def _is_expiring(self, token: str) -> bool:
        """
        Проверяет на истечение токена.
        """
        
        payload = self._decode(token)
        exp_ts = payload.get('exp')
        if exp_ts is None:
            return True
        
        exp = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        leeway = timedelta(minutes=self.leeway_minutes)
        return exp - now <= leeway
    
    def _calc_ttl(self, token: str) -> int:
        """
        Возвращает ttl токена в секундах с запасом.
        """
        
        payload = self._decode(token)
        exp_ts = payload.get('exp')
        if exp_ts is None:
            return 0
        
        exp = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        ttl = int((exp - now).total_seconds()) - self.leeway_minutes * 60
        return max(ttl, 0)
        