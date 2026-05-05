"""004_create_plans

Revision ID: de6edac4518f
Revises: d50716bebe1f
Create Date: 2026-03-18 15:51:08.078777

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

UTC = timezone.utc


# revision identifiers, used by Alembic.
revision = 'de6edac4518f'
down_revision = 'd50716bebe1f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('preco_mensal_centavos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('moeda', sa.String(length=8), nullable=False, server_default='brl'),
        sa.Column('stripe_price_id', sa.String(length=120), nullable=True),
        sa.Column('limite_playlists_privadas', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('limite_usuarios', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_plans_codigo', 'plans', ['codigo'], unique=True)
    op.create_index('ix_plans_stripe_price_id', 'plans', ['stripe_price_id'], unique=True)

    connection = op.get_bind()
    now = datetime.now(UTC)
    connection.execute(
        sa.text(
            """
            INSERT INTO plans
            (codigo, nome, descricao, preco_mensal_centavos, moeda, limite_playlists_privadas, limite_usuarios, ativo, data_criacao)
            VALUES
            (:codigo_free, :nome_free, :descricao_free, :preco_free, :moeda, :limite_free_playlist, :limite_free_usuarios, :ativo, :data),
            (:codigo_pro, :nome_pro, :descricao_pro, :preco_pro, :moeda, :limite_pro_playlist, :limite_pro_usuarios, :ativo, :data)
            """
        ),
        {
            'codigo_free': 'free',
            'nome_free': 'Free',
            'descricao_free': 'Plano inicial',
            'preco_free': 0,
            'codigo_pro': 'pro',
            'nome_pro': 'Pro',
            'descricao_pro': 'Plano de crescimento',
            'preco_pro': 4900,
            'moeda': 'brl',
            'limite_free_playlist': 1,
            'limite_free_usuarios': 1,
            'limite_pro_playlist': 25,
            'limite_pro_usuarios': 5,
            'ativo': True,
            'data': now,
        },
    )


def downgrade():
    op.drop_index('ix_plans_stripe_price_id', table_name='plans')
    op.drop_index('ix_plans_codigo', table_name='plans')
    op.drop_table('plans')
