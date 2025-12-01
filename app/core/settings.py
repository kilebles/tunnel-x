from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Читает переменные окружения и предоставляет настройки приложения.
    """

    BOT_TOKEN: str
    BASE_URL: str
    TELEGRAM_WEBHOOK_PATH: str = '/webhook/telegram'
    REDIS_URL: str = 'redis://redis:6379/0'
    
    PANEL_URL: str
    PANEL_TOKEN: str | None = None
    PANEL_LOGIN: str
    PANEL_PASSWORD: str
    
    DEFAULT_SQUAD_ID: str = '0b93d216-44d4-41ee-9a90-831bd6c02f9a'
    
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    class Config:
        env_file = '.env'

    @property
    def TELEGRAM_WEBHOOK(self) -> str:
        return f"{self.BASE_URL}{self.TELEGRAM_WEBHOOK_PATH}"
    
    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )
    
    
config = Settings()