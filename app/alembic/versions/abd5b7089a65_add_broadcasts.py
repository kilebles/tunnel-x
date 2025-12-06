"""add_broadcasts

Revision ID: abd5b7089a65
Revises: 29e14361b386
Create Date: 2025-12-05 18:58:08.092384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abd5b7089a65'
down_revision: Union[str, Sequence[str], None] = '29e14361b386'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'broadcasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('broadcasts')