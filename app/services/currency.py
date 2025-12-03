from httpx import AsyncClient
from loguru import logger


class CurrencyService:
    """Сервис для работы с курсами валют."""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self._cached_rate = 95.0  # Кэш на случай недоступности API
    
    async def get_usd_to_rub_rate(self) -> float:
        """
        Получает актуальный курс USD -> RUB.
        В случае ошибки возвращает кэшированное значение.
        """
        try:
            async with AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/USD")
                response.raise_for_status()
                data = response.json()
                
                rate = data['rates'].get('RUB', 95.0)
                self._cached_rate = rate  # Обновляем кэш
                
                logger.debug(f'Получен курс USD->RUB: {rate}')
                return rate
                
        except Exception as e:
            logger.warning(f'Ошибка получения курса валют: {e}. Используем кэш: {self._cached_rate}')
            return self._cached_rate
    
    async def convert_rub_to_usd(self, rub: int) -> float:
        """Конвертирует рубли в доллары."""
        rate = await self.get_usd_to_rub_rate()
        return round(rub / rate, 2)