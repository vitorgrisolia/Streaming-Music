"""003_create_memberships_and_composite_uniques

Revision ID: d50716bebe1f
Revises: 574144984d1b
Create Date: 2026-03-17 17:20:52.258717

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

UTC = timezone.utc


# revision identifiers, used by Alembic.
revision = 'd50716bebe1f'
down_revision = '574144984d1b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenant_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='member'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'user_id', name='uq_tenant_membership_tenant_user'),
    )
    op.create_index('ix_tenant_memberships_tenant_id', 'tenant_memberships', ['tenant_id'], unique=False)
    op.create_index('ix_tenant_memberships_user_id', 'tenant_memberships', ['user_id'], unique=False)

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO tenant_memberships (tenant_id, user_id, role, ativo, data_criacao)
            SELECT usuarios.tenant_id, usuarios.id, :role, :ativo, :data_criacao
            FROM usuarios
            """
        ),
        {
            'role': 'owner',
            'ativo': True,
            'data_criacao': datetime.now(UTC),
        },
    )

    with op.batch_alter_table('playlists', schema=None) as batch_op:
        batch_op.create_unique_constraint(
            'uq_playlists_tenant_usuario_nome',
            ['tenant_id', 'usuario_id', 'nome'],
        )


def downgrade():
    with op.batch_alter_table('playlists', schema=None) as batch_op:
        batch_op.drop_constraint('uq_playlists_tenant_usuario_nome', type_='unique')

    op.drop_index('ix_tenant_memberships_user_id', table_name='tenant_memberships')
    op.drop_index('ix_tenant_memberships_tenant_id', table_name='tenant_memberships')
    op.drop_table('tenant_memberships')
