from decimal import Decimal

from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from loguru import logger


class BalanceService:
    """Управление балансом пользователей."""
    
    async def set_balance(self, telegram_id: int, amount: float) -> Decimal:
        """Устанавливает баланс пользователя."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            await session.refresh(user, ['wallet'])
            user.wallet.balance = Decimal(str(amount))
            
            await session.commit()
            
            logger.info(f'Баланс установлен: tg_id={telegram_id}, balance={amount}')
            
            return user.wallet.balance
    
    async def add_balance(self, telegram_id: int, amount: float) -> Decimal:
        """Добавляет средства к балансу."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            await session.refresh(user, ['wallet'])
            user.wallet.balance += Decimal(str(amount))
            
            await session.commit()
            
            logger.info(f'Баланс пополнен: tg_id={telegram_id}, added={amount}, new_balance={user.wallet.balance}')
            
            return user.wallet.balance
    
    async def subtract_balance(self, telegram_id: int, amount: float) -> Decimal:
        """Списывает средства с баланса."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            await session.refresh(user, ['wallet'])
            
            if user.wallet.balance < Decimal(str(amount)):
                raise ValueError('Недостаточно средств на балансе')
            
            user.wallet.balance -= Decimal(str(amount))
            
            await session.commit()
            
            logger.info(f'Баланс списан: tg_id={telegram_id}, subtracted={amount}, new_balance={user.wallet.balance}')
            
            return user.wallet.balance
    
    async def get_balance(self, telegram_id: int) -> Decimal:
        """Получает текущий баланс пользователя."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            await session.refresh(user, ['wallet'])
            return user.wallet.balance
