"""added GCO tables

Revision ID: 661523710261
Revises: 9581690db090
Create Date: 2025-08-24 23:46:33.070020
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '661523710261'
down_revision: Union[str, Sequence[str], None] = '9581690db090'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'graduate_career_opportunities',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('university_code', sa.String(), nullable=False),
        sa.Column('specialty_code', sa.String(), nullable=False),
        sa.Column('career_code', sa.String(), nullable=False, unique=True),
        sa.ForeignKeyConstraint(['specialty_code'], ['specialties.specialty_code']),
        sa.ForeignKeyConstraint(['university_code'], ['universities.university_code'])
    )
    op.create_index(
        op.f('ix_graduate_career_opportunities_id'),
        'graduate_career_opportunities',
        ['id'],
        unique=False
    )

    op.create_table(
        'graduate_career_opportunities_translations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('career_code', sa.String(), nullable=False),
        sa.Column('language_code', sa.CHAR(length=2), nullable=False),
        sa.Column('career_content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['career_code'], ['graduate_career_opportunities.career_code'])
    )
    op.create_index(
        op.f('ix_graduate_career_opportunities_translations_id'),
        'graduate_career_opportunities_translations',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_graduate_career_opportunities_translations_id'),
        table_name='graduate_career_opportunities_translations'
    )
    op.drop_table('graduate_career_opportunities_translations')

    op.drop_index(
        op.f('ix_graduate_career_opportunities_id'),
        table_name='graduate_career_opportunities'
    )
    op.drop_table('graduate_career_opportunities')
