"""
Настройка для логирования приложения.
"""

from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    level: str = 'INFO'
    log_file: str = 'logs/app.log'
    rotation: str = '10 MB'
    retention: str = '7 days'
    compression: str = 'zip'

    class Config:
        env_prefix = 'LOGGER_'