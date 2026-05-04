"""added speciality_characteristics and speciality_characteristics_translation

Revision ID: e74bedfef6dc
Revises: bf520b9d671a
Create Date: 2025-08-25 19:06:51.880719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e74bedfef6dc'
down_revision: Union[str, Sequence[str], None] = 'bf520b9d671a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'speciality_characteristics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('specialty_code', sa.String(), nullable=False),
        sa.Column('characteristic_code', sa.String(), nullable=False, unique=True),
        sa.ForeignKeyConstraint(['specialty_code'], ['specialties.specialty_code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_speciality_characteristics_id'), 'speciality_characteristics', ['id'], unique=False)

    op.create_table(
        'speciality_characteristics_translation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('characteristic_code', sa.String(), nullable=False),
        sa.Column('language_code', sa.CHAR(length=2), nullable=False),
        sa.Column('characteristic_content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['characteristic_code'], ['speciality_characteristics.characteristic_code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_speciality_characteristics_translation_id'),
        'speciality_characteristics_translation',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop speciality_characteristics_translation table
    op.drop_index(
        op.f('ix_speciality_characteristics_translation_id'),
        table_name='speciality_characteristics_translation'
    )
    op.drop_table('speciality_characteristics_translation')

    # Drop speciality_characteristics table
    op.drop_index(
        op.f('ix_speciality_characteristics_id'),
        table_name='speciality_characteristics'
    )
    op.drop_table('speciality_characteristics')
