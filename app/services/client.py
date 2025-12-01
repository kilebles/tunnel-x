from httpx import AsyncClient, HTTPStatusError
from app.core.settings import config


class PanelError(Exception):
    """
    Ошибка при работе с панелью
    """

class PanelClient:
    """
    HTTP клиент для работы с клиентом
    """
    
    def __init__(self):
        self.base_url = config.PANEL_URL.rstrip('/')
        self.token = config.PANEL_TOKEN

    async def request(self, method: str, path: str, **kwargs):
        headers = kwargs.pop('headers', {}) or {}
        headers['Authorization'] = f'Bearer {self.token}'
        headers['Content-Type'] = 'application/json'

        url = f'{self.base_url}{path}'


        try:
            async with AsyncClient(timeout=10) as client:
                response = await client.request(
                    method, 
                    url, 
                    headers=headers, 
                    timeout=10, 
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
        except HTTPStatusError as e:
            raise PanelError(f'{method} {path}: {e.response.status.code}')
        except Exception as e:
            raise PanelError(f'{method} {path}: {e}')