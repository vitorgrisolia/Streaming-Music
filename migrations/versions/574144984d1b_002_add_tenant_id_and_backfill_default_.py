"""002_add_tenant_id_and_backfill_default_tenant

Revision ID: 574144984d1b
Revises: 79436e86c751
Create Date: 2026-03-17 17:20:46.256125

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

UTC = timezone.utc


# revision identifiers, used by Alembic.
revision = '574144984d1b'
down_revision = '79436e86c751'
branch_labels = None
depends_on = None


def _ensure_default_tenant(connection):
    slug = 'default'
    tenant_id = connection.execute(
        sa.text('SELECT id FROM tenants WHERE slug = :slug'),
        {'slug': slug},
    ).scalar()
    if tenant_id is not None:
        return tenant_id

    connection.execute(
        sa.text(
            """
            INSERT INTO tenants (nome, slug, ativo, data_criacao)
            VALUES (:nome, :slug, :ativo, :data_criacao)
            """
        ),
        {
            'nome': 'Workspace Padrao',
            'slug': slug,
            'ativo': True,
            'data_criacao': datetime.now(UTC),
        },
    )
    return connection.execute(
        sa.text('SELECT id FROM tenants WHERE slug = :slug'),
        {'slug': slug},
    ).scalar()


def upgrade():
    connection = op.get_bind()
    tenant_id = _ensure_default_tenant(connection)

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_usuarios_tenant_id', ['tenant_id'], unique=False)

    connection.execute(
        sa.text('UPDATE usuarios SET tenant_id = :tenant_id WHERE tenant_id IS NULL'),
        {'tenant_id': tenant_id},
    )

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            'fk_usuarios_tenant_id_tenants',
            'tenants',
            ['tenant_id'],
            ['id'],
        )

    with op.batch_alter_table('playlists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_playlists_tenant_id', ['tenant_id'], unique=False)

    connection.execute(
        sa.text(
            """
            UPDATE playlists
            SET tenant_id = (
                SELECT usuarios.tenant_id
                FROM usuarios
                WHERE usuarios.id = playlists.usuario_id
            )
            WHERE tenant_id IS NULL
            """
        )
    )
    connection.execute(
        sa.text('UPDATE playlists SET tenant_id = :tenant_id WHERE tenant_id IS NULL'),
        {'tenant_id': tenant_id},
    )

    with op.batch_alter_table('playlists', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            'fk_playlists_tenant_id_tenants',
            'tenants',
            ['tenant_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('playlists', schema=None) as batch_op:
        batch_op.drop_constraint('fk_playlists_tenant_id_tenants', type_='foreignkey')
        batch_op.drop_index('ix_playlists_tenant_id')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_usuarios_tenant_id_tenants', type_='foreignkey')
        batch_op.drop_index('ix_usuarios_tenant_id')
        batch_op.drop_column('tenant_id')
