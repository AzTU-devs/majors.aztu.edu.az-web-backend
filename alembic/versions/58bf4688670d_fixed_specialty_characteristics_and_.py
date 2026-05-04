"""fixed specialty_characteristics and specialty_characteristics_translations

Revision ID: 58bf4688670d
Revises: e74bedfef6dc
Create Date: 2025-08-25 22:21:11.398708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '58bf4688670d'
down_revision: Union[str, Sequence[str], None] = 'e74bedfef6dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'specialty_characteristics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('specialty_code', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['specialty_code'], ['specialties.specialty_code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_specialty_characteristics_id'),
        'specialty_characteristics',
        ['id'],
        unique=False
    )

    op.create_table(
        'specialty_characteristics_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('specialty_code', sa.String(), nullable=False),
        sa.Column('language_code', sa.CHAR(length=2), nullable=False),
        sa.Column('program_desc', sa.String(), nullable=True),
        sa.Column('degree_requirements', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['specialty_code'], ['specialties.specialty_code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_specialty_characteristics_translations_id'),
        'specialty_characteristics_translations',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop specialty_characteristics_translations table
    op.drop_index(
        op.f('ix_specialty_characteristics_translations_id'),
        table_name='specialty_characteristics_translations'
    )
    op.drop_table('specialty_characteristics_translations')

    # Drop specialty_characteristics table
    op.drop_index(
        op.f('ix_specialty_characteristics_id'),
        table_name='specialty_characteristics'
    )
    op.drop_table('specialty_characteristics')
