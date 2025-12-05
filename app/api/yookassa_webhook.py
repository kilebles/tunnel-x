from fastapi import APIRouter, Request, HTTPException
from loguru import logger

from app.services.payment import PaymentService

router = APIRouter()


@router.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    """Обрабатывает вебхуки от ЮKassa."""
    try:
        payload = await request.json()
        event = payload.get('event')
        obj = payload.get('object', {})
        
        logger.info(f'Получен вебхук ЮKassa: event={event}, payment_id={obj.get("id")}')
        
        if event == 'payment.succeeded':
            payment_service = PaymentService()
            
            payment_data = {
                'id': obj.get('id'),
                'status': obj.get('status'),
                'paid': obj.get('paid'),
                'amount': obj.get('amount', {}).get('value'),
                'metadata': obj.get('metadata', {})
            }
            
            await payment_service.process_successful_card_payment(payment_data)
            
            logger.info(f'Платёж успешно обработан: payment_id={payment_data["id"]}')
        
        elif event == 'payment.canceled':
            logger.info(f'Платёж отменён: payment_id={obj.get("id")}')
        
        return {"status": "ok"}
        
    except Exception:
        logger.exception('Ошибка обработки вебхука ЮKassa')
        raise HTTPException(status_code=500, detail='Internal server error')