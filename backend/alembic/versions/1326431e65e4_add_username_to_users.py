"""add_username_to_users

Revision ID: 1326431e65e4
Revises: a927927f25d6
Create Date: 2026-08-03 20:13:55.349727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1326431e65e4'
down_revision: Union[str, Sequence[str], None] = 'a927927f25d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "username",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_users_username",
        table_name="users",
    )

    op.drop_column(
        "users",
        "username",
    )
