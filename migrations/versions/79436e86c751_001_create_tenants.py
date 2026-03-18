"""001_create_tenants

Revision ID: 79436e86c751
Revises: 
Create Date: 2026-03-17 17:20:39.119266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79436e86c751'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)


def downgrade():
    op.drop_index('ix_tenants_slug', table_name='tenants')
    op.drop_table('tenants')
