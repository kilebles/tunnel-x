from uuid import uuid4
from yookassa import Configuration, Payment
from loguru import logger

from app.core.settings import config

Configuration.configure(config.YOOKASSA_ACCOUNT_ID, config.YOOKASSA_SECRET_KEY)


class YooKassaService:
    """Сервис для работы с ЮKassa."""
    
    async def create_payment(
        self,
        amount: int,
        description: str,
        telegram_id: int,
        devices: int,
        days: int
    ) -> dict:
        """
        Создаёт платёж в ЮKassa.
        Возвращает payment_id и confirmation_url.
        """
        try:
            idempotence_key = str(uuid4())
            
            payment = Payment.create({
                "amount": {
                    "value": f"{amount}.00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"https://t.me/{config.BOT_TOKEN.split(':')[0]}"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "telegram_id": str(telegram_id),
                    "devices": str(devices),
                    "days": str(days)
                }
            }, idempotence_key)
            
            logger.info(
                f'Создан платёж ЮKassa: payment_id={payment.id}, '
                f'amount={amount}, tg_id={telegram_id}'
            )
            
            return {
                "payment_id": payment.id,
                "confirmation_url": payment.confirmation.confirmation_url,
                "status": payment.status
            }
            
        except Exception as e:
            logger.exception(f'Ошибка создания платежа ЮKassa для tg_id={telegram_id}')
            raise
    
    async def get_payment_info(self, payment_id: str) -> dict:
        """Получает информацию о платеже."""
        try:
            payment = Payment.find_one(payment_id)
            
            return {
                "id": payment.id,
                "status": payment.status,
                "paid": payment.paid,
                "amount": float(payment.amount.value),
                "metadata": payment.metadata
            }
            
        except Exception as e:
            logger.exception(f'Ошибка получения информации о платеже {payment_id}')
            raise