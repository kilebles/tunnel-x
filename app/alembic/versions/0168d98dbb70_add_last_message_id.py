"""add_last_message_id

Revision ID: 0168d98dbb70
Revises: 5710b1c80017
Create Date: 2025-12-04 xx:xx:xx
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0168d98dbb70'
down_revision: Union[str, Sequence[str], None] = '5710b1c80017'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('last_message_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_message_id')