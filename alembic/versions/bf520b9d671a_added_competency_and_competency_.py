"""added competency and competency_translations

Revision ID: bf520b9d671a
Revises: 661523710261
Create Date: 2025-08-25 16:20:17.092294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bf520b9d671a'
down_revision: Union[str, Sequence[str], None] = '661523710261'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'competency',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('university_code', sa.String(), nullable=False),
        sa.Column('specialty_code', sa.String(), nullable=False),
        sa.Column('competency_code', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['specialty_code'], ['specialties.specialty_code']),
        sa.ForeignKeyConstraint(['university_code'], ['universities.university_code']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('competency_code')
    )
    op.create_index(op.f('ix_competency_id'), 'competency', ['id'], unique=False)

    op.create_table(
        'competency_translation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('competency_code', sa.String(), nullable=False),
        sa.Column('language_code', sa.CHAR(length=2), nullable=False),
        sa.Column('competency_content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['competency_code'], ['competency.competency_code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competency_translation_id'), 'competency_translation', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop competency_translation table
    op.drop_index(op.f('ix_competency_translation_id'), table_name='competency_translation')
    op.drop_table('competency_translation')

    # Drop competency table
    op.drop_index(op.f('ix_competency_id'), table_name='competency')
    op.drop_table('competency')
