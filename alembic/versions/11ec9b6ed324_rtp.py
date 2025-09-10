"""rtp

Revision ID: 11ec9b6ed324
Revises: 1c1e8885a654
Create Date: 2025-09-10 05:46:38.334469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11ec9b6ed324'
down_revision: Union[str, Sequence[str], None] = '1c1e8885a654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
