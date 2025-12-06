from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Discount, PromoCode
from loguru import logger


class DiscountService:
    """Сервис работы со скидками и промокодами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_active_global_discount(self) -> int:
        """Получить активную глобальную скидку в процентах."""
        result = await self.session.execute(
            select(Discount.percentage)
            .where(Discount.is_active == True)
            .order_by(Discount.created_at.desc())
            .limit(1)
        )
        discount = result.scalar_one_or_none()
        return discount or 0
    
    async def validate_promo_code(self, code: str) -> tuple[bool, int, str]:
        """
        Валидирует промокод.
        
        Returns:
            (is_valid, percentage, error_message)
        """
        result = await self.session.execute(
            select(PromoCode)
            .where(PromoCode.code == code.upper())
        )
        promo = result.scalar_one_or_none()
        
        if not promo:
            return False, 0, "Промокод не найден"
        
        if not promo.is_active:
            return False, 0, "Промокод неактивен"
        
        if promo.expires_at and promo.expires_at < datetime.now(timezone.utc):
            return False, 0, "Промокод истёк"
        
        if promo.max_uses and promo.used_count >= promo.max_uses:
            return False, 0, "Промокод исчерпан"
        
        return True, promo.percentage, ""
    
    async def use_promo_code(self, code: str) -> int:
        """Использует промокод, возвращает процент скидки."""
        is_valid, percentage, error = await self.validate_promo_code(code)
        
        if not is_valid:
            raise ValueError(error)
        
        result = await self.session.execute(
            select(PromoCode)
            .where(PromoCode.code == code.upper())
        )
        promo = result.scalar_one()
        
        promo.used_count += 1
        await self.session.flush()
        
        logger.info(f'Промокод {code} использован, теперь {promo.used_count}/{promo.max_uses or "∞"}')
        
        return percentage