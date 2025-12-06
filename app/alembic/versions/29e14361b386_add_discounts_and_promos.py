"""add_discounts_and_promos

Revision ID: 29e14361b386
Revises: 0168d98dbb70
Create Date: 2025-12-05 18:25:29.811767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29e14361b386'
down_revision: Union[str, Sequence[str], None] = '0168d98dbb70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Таблица глобальных скидок
    op.create_table(
        'discounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('percentage', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_discounts_is_active', 'discounts', ['is_active'])
    
    # Таблица промокодов
    op.create_table(
        'promo_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('percentage', sa.Integer(), nullable=False),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_promo_codes_code', 'promo_codes', ['code'])
    op.create_index('ix_promo_codes_is_active', 'promo_codes', ['is_active'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_promo_codes_is_active', table_name='promo_codes')
    op.drop_index('ix_promo_codes_code', table_name='promo_codes')
    op.drop_table('promo_codes')
    
    op.drop_index('ix_discounts_is_active', table_name='discounts')
    op.drop_table('discounts')
