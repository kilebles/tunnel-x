"""add_broadcast_button_texts

Revision ID: de4e1021b916
Revises: ceb45cbdf5ca
Create Date: 2025-12-05 19:33:47.863179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de4e1021b916'
down_revision: Union[str, Sequence[str], None] = 'ceb45cbdf5ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('broadcasts', sa.Column('community_button_text', sa.String(length=100), nullable=True, server_default='👥 Сообщество'))
    op.add_column('broadcasts', sa.Column('try_button_text', sa.String(length=100), nullable=True, server_default='🚀 Попробовать'))
    op.alter_column('broadcasts', 'community_url', server_default='https://t.me/TunnelX_News')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('broadcasts', 'try_button_text')
    op.drop_column('broadcasts', 'community_button_text')
    op.alter_column('broadcasts', 'community_url', server_default=None)