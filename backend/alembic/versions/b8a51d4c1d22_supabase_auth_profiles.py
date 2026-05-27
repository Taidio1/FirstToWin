"""supabase auth profiles
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8a51d4c1d22"
down_revision: Union[str, Sequence[str], None] = "a3f8e21c9d04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("supabase_user_id", sa.String(), nullable=True))
    op.create_unique_constraint(
        "uq_user_supabase_user_id",
        "user",
        ["supabase_user_id"],
    )
    op.alter_column("user", "password", existing_type=sa.String(), nullable=True)
    op.execute("UPDATE \"user\" SET role = 'user' WHERE role IN ('viewer', 'analyst')")
    op.execute("UPDATE \"user\" SET role = 'admin' WHERE email = 'demo@example.local'")


def downgrade() -> None:
    op.execute("UPDATE \"user\" SET password = '' WHERE password IS NULL")
    op.alter_column("user", "password", existing_type=sa.String(), nullable=False)
    op.drop_constraint("uq_user_supabase_user_id", "user", type_="unique")
    op.drop_column("user", "supabase_user_id")
