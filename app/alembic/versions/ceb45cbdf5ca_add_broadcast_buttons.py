"""add_broadcast_buttons

Revision ID: ceb45cbdf5ca
Revises: abd5b7089a65
Create Date: 2025-12-05 19:11:28.898718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceb45cbdf5ca'
down_revision: Union[str, Sequence[str], None] = 'abd5b7089a65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('broadcasts', sa.Column('add_community_button', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('broadcasts', sa.Column('community_url', sa.String(length=255), nullable=True))
    op.add_column('broadcasts', sa.Column('add_try_button', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('broadcasts', 'add_try_button')
    op.drop_column('broadcasts', 'community_url')
    op.drop_column('broadcasts', 'add_community_button')