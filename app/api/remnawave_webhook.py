import hmac
import hashlib
import json

from fastapi import APIRouter, Request, HTTPException
from loguru import logger

from app.core.settings import config
from app.services.remnawave_webhook import WebhookService

router = APIRouter()


def validate_webhook(body: bytes, signature: str) -> bool:
    """Проверяет подпись вебхука."""
    computed_signature = hmac.new(
        config.WEBHOOK_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


@router.post("/webhook/remnawave")
async def remnawave_webhook(request: Request):
    """Обрабатывает вебхуки от Remnawave."""
    
    signature = request.headers.get('x-remnawave-signature')
    timestamp = request.headers.get('x-remnawave-timestamp')
    
    if not signature:
        logger.warning('Вебхук без подписи')
        raise HTTPException(status_code=401, detail='Missing signature')
    
    body = await request.body()
    
    if not validate_webhook(body, signature):
        logger.warning('Неверная подпись вебхука')
        raise HTTPException(status_code=401, detail='Invalid signature')
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error('Невалидный JSON в вебхуке')
        raise HTTPException(status_code=400, detail='Invalid JSON')
    
    event = payload.get('event')
    data = payload.get('data')
    
    logger.info(f'Получен вебхук: event={event}, timestamp={timestamp}')

    service = WebhookService()
    await service.handle_event(event, data)
    
    return {"ok": True}