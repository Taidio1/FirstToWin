"""add info severity

Revision ID: c01e8805a5bc
Revises: 7a3fd8d3a0b1
Create Date: 2026-05-23 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c01e8805a5bc"
down_revision: Union[str, Sequence[str], None] = "7a3fd8d3a0b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE severity ADD VALUE IF NOT EXISTS 'info'")


def downgrade() -> None:
    pass
