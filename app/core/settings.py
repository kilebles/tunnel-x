from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Читает переменные окружения и предоставляет настройки приложения.
    """

    BOT_TOKEN: str
    BASE_URL: str
    TELEGRAM_WEBHOOK_PATH: str = '/webhook/telegram'
    REDIS_URL: str = 'redis://redis:6379/0'

    class Config:
        env_file = '.env'

    @property
    def TELEGRAM_WEBHOOK(self) -> str:
        return f"{self.BASE_URL}{self.TELEGRAM_WEBHOOK_PATH}"
    
    
config = Settings()