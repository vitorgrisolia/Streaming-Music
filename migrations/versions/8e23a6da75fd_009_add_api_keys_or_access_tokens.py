"""009_add_api_keys_or_access_tokens

Revision ID: 8e23a6da75fd
Revises: f4e2e599a4a8
Create Date: 2026-03-18 15:51:39.608562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e23a6da75fd'
down_revision = 'f4e2e599a4a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=80), nullable=False),
        sa.Column('chave_hash', sa.String(length=128), nullable=False),
        sa.Column('prefixo', sa.String(length=12), nullable=False),
        sa.Column('ultimo_uso_em', sa.DateTime(), nullable=True),
        sa.Column('expira_em', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chave_hash'),
    )
    op.create_index('ix_api_keys_tenant_id', 'api_keys', ['tenant_id'], unique=False)
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'], unique=False)
    op.create_index('ix_api_keys_chave_hash', 'api_keys', ['chave_hash'], unique=True)
    op.create_index('ix_api_keys_prefixo', 'api_keys', ['prefixo'], unique=False)


def downgrade():
    op.drop_index('ix_api_keys_prefixo', table_name='api_keys')
    op.drop_index('ix_api_keys_chave_hash', table_name='api_keys')
    op.drop_index('ix_api_keys_user_id', table_name='api_keys')
    op.drop_index('ix_api_keys_tenant_id', table_name='api_keys')
    op.drop_table('api_keys')
