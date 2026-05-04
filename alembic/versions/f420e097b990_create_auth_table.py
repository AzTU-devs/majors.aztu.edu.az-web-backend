"""create auth table

Revision ID: f420e097b990
Revises: 
Create Date: 2025-08-17 23:41:31.419561
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f420e097b990'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'auth',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('fin_kod', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
        sa.Column('otp', sa.Integer(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_auth_id'), 'auth', ['id'], unique=False)

    op.alter_column('cafedras', 'university_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('cafedras', 'faculty_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('cafedras', 'cafedra_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('cafedras', 'cafedra_name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('cafedras', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.create_index(op.f('ix_cafedras_id'), 'cafedras', ['id'], unique=False)

    op.alter_column('faculties', 'university_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('faculties', 'faculty_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('faculties', 'faculty_name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('faculties', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.create_index(op.f('ix_faculties_id'), 'faculties', ['id'], unique=False)

    op.alter_column('specialties', 'university_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('specialties', 'cafedra_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('specialties', 'specialty_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('specialties', 'specialty_name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.create_index(op.f('ix_specialties_id'), 'specialties', ['id'], unique=False)

    op.alter_column('universities', 'university_code',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('universities', 'university_name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('universities', 'university_short_name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.create_index(op.f('ix_universities_id'), 'universities', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_universities_id'), table_name='universities')
    op.alter_column('universities', 'university_short_name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('universities', 'university_name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('universities', 'university_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.drop_index(op.f('ix_specialties_id'), table_name='specialties')
    op.alter_column('specialties', 'specialty_name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('specialties', 'specialty_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('specialties', 'cafedra_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('specialties', 'university_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.drop_index(op.f('ix_faculties_id'), table_name='faculties')
    op.alter_column('faculties', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('faculties', 'faculty_name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('faculties', 'faculty_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('faculties', 'university_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.drop_index(op.f('ix_cafedras_id'), table_name='cafedras')
    op.alter_column('cafedras', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('cafedras', 'cafedra_name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('cafedras', 'cafedra_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('cafedras', 'faculty_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('cafedras', 'university_code',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.drop_index(op.f('ix_auth_id'), table_name='auth')
    op.drop_table('auth')
