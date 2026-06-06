"""add_alert_fingerprint_count_last_seen

Revision ID: a3f8e21c9d04
Revises: ddfe7375dbba
Create Date: 2026-05-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f8e21c9d04'
down_revision: Union[str, Sequence[str], None] = 'ddfe7375dbba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('fingerprint', sa.String(), nullable=False, server_default=''))
    op.add_column('alerts', sa.Column('count', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('alerts', sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'last_seen')
    op.drop_column('alerts', 'count')
    op.drop_column('alerts', 'fingerprint')
