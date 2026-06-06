"""add sensor api key

Revision ID: 58d8f0e4a1b2
Revises: c01e8805a5bc
Create Date: 2026-05-23 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "58d8f0e4a1b2"
down_revision: Union[str, Sequence[str], None] = "c01e8805a5bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sensors",
        sa.Column("api_key", sa.String(), nullable=False, server_default=""),
    )
    op.execute(
        "UPDATE sensors SET api_key = 'demo-sensor-key' WHERE name = 'local-demo-sensor'"
    )
    op.alter_column("sensors", "api_key", server_default=None)


def downgrade() -> None:
    op.drop_column("sensors", "api_key")
