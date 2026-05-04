"""Add SpecialtyCharacteristics and translations ForeignKey

Revision ID: 8ebd815fccb0
Revises: 58bf4688670d
Create Date: 2025-08-26 01:32:54.467307
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8ebd815fccb0'
down_revision: Union[str, Sequence[str], None] = '58bf4688670d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'specialty_characteristics_translations',
        sa.Column('specialty_characteristic_id', sa.Integer(), nullable=False)
    )

    op.drop_constraint(
        'specialty_characteristics_translations_specialty_code_fkey',
        'specialty_characteristics_translations',
        type_='foreignkey'
    )

    op.create_foreign_key(
        None,
        'specialty_characteristics_translations',
        'specialty_characteristics',
        ['specialty_characteristic_id'],
        ['id']
    )

    op.drop_column('specialty_characteristics_translations', 'specialty_code')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'specialty_characteristics_translations',
        sa.Column('specialty_code', sa.String(), nullable=False)
    )

    op.drop_constraint(
        None,
        'specialty_characteristics_translations',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'specialty_characteristics_translations_specialty_code_fkey',
        'specialty_characteristics_translations',
        'specialties',
        ['specialty_code'],
        ['specialty_code']
    )

    op.drop_column('specialty_characteristics_translations', 'specialty_characteristic_id')
