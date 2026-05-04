"""merge auth and slo/plo heads

Revision ID: 9581690db090
Revises: 65b3baddaf16, 15e6262efce9
Create Date: 2025-08-23 23:06:01.570680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9581690db090'
down_revision: Union[str, Sequence[str], None] = ('65b3baddaf16', '15e6262efce9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
