from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Читает переменные окружения и предоставляет настройки приложения.
    """

    BOT_TOKEN: str
    BASE_URL: str
    REDIS_URL: str = 'redis://redis:6379/0'
    
    # Переменные RW
    PANEL_URL: str
    PANEL_TOKEN: str | None = None
    PANEL_LOGIN: str
    PANEL_PASSWORD: str
    WEBHOOK_SECRET: str
    
    YOOKASSA_ACCOUNT_ID: str
    YOOKASSA_SECRET_KEY: str
    
    # Внутренние сквады
    INTERNAL_SQUAD_MAIN: str = '0b93d216-44d4-41ee-9a90-831bd6c02f9a'
    INTERNAL_SQUAD_FREE: str = '22598026-ee8c-4e2f-86ce-ab502c8d387b'
    
    # Внешние сквады
    EXTERNAL_SQUAD_PREMIUM: str = 'fa810a74-84ce-43c7-8aa7-031300453385'
    EXTERNAL_SQUAD_FREE: str = '5499389e-b53b-44f0-a7b5-19d6bfc55064'
    
    # Настройки триала
    TRIAL_DAYS: int = 2
    
    # Переменные БД
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Админ панель
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    SECRET_KEY: str

    class Config:
        env_file = '.env'

    @property
    def TELEGRAM_WEBHOOK(self) -> str:
        return f"{self.BASE_URL}/webhook/telegram"
    
    @property
    def REMNAWAVE_WEBHOOK(self) -> str:
        return f"{self.BASE_URL}/webhook/remnawave"
    
    @property
    def YOOKASSA_WEBHOOK(self) -> str:
        return f"{self.BASE_URL}/webhook/yookassa"
    
    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )
    
    
config = Settings()