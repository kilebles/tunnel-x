"""
Клиент панели: делает запросы с фиксированным токеном.
"""

from httpx import AsyncClient
from app.core.settings import config


class PanelClient:
    def __init__(self):
        self.base_url = config.PANEL_URL.rstrip('/')
        self.token = config.PANEL_TOKEN

    async def request(self, method: str, path: str, **kwargs):
        headers = kwargs.pop('headers', {}) or {}
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"

        url = f"{self.base_url}{path}"

        async with AsyncClient() as client:
            response = await client.request(
                method, 
                url, 
                headers=headers, 
                timeout=10, 
                **kwargs
            )
            response.raise_for_status()
            return response.json()