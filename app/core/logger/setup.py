"""
Логирование через loguru.
"""

import logging

from pathlib import Path
from loguru import logger

from app.core.logger.config import LoggerSettings

class InterceptHandler(logging.Handler):
    """Хендлер для преенаправления стд. логов в loguru"""
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = 'INFO'
        
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())
        

def setup_logger() -> None:
    """
    Конфигурирация логирования
    """

    settings = LoggerSettings()
    print('CWD:', Path.cwd())
    print('Writing to:', settings.log_file)

    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sink=settings.log_file,
        level=settings.level,
        rotation=settings.rotation,
        retention=settings.retention,
        compression=settings.compression,
        enqueue=True,
        backtrace=True,
        diagnose=True
    )

    logger.add(
        sink=lambda msg: print(msg, end=''),
        level=settings.level,
        enqueue=True,
        backtrace=True,
        diagnose=False
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in (
        'uvicorn',
        'uvicorn.error',
        'uvicorn.access',
        'fastapi',
        'sqlalchemy',
        'aiogram'
    ):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
    
    