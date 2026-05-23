"""add alert details

Revision ID: 7a3fd8d3a0b1
Revises: 0277fb020be9
Create Date: 2026-05-23 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a3fd8d3a0b1"
down_revision: Union[str, Sequence[str], None] = "0277fb020be9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "alerts",
        sa.Column("details", sa.String(), nullable=False, server_default=""),
    )
    op.alter_column("alerts", "details", server_default=None)


def downgrade() -> None:
    op.drop_column("alerts", "details")
