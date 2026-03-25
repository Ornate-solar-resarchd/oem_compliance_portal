"""Initial schema baseline (created via schema.sql)

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The initial database schema was applied directly via schema.sql.
    # This migration exists only to establish a baseline for Alembic's
    # version tracking.  Run `alembic stamp 001_initial` on existing
    # databases instead of `alembic upgrade`.
    pass


def downgrade() -> None:
    # Nothing to do — the schema was created outside of Alembic.
    pass
