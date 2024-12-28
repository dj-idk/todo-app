"""Create phone number for user table

Revision ID: b0b9a24aa2e5
Revises: 
Create Date: 2024-12-28 09:43:38.035797

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b0b9a24aa2e5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("phone_number", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "phone_number")
