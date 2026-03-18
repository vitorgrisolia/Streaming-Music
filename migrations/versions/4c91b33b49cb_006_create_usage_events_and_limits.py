"""006_create_usage_events_and_limits

Revision ID: 4c91b33b49cb
Revises: c680ff7bb836
Create Date: 2026-03-18 15:51:19.998661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c91b33b49cb'
down_revision = 'c680ff7bb836'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'usage_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=80), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_usage_events_tenant_id', 'usage_events', ['tenant_id'], unique=False)
    op.create_index('ix_usage_events_user_id', 'usage_events', ['user_id'], unique=False)
    op.create_index('ix_usage_events_event_type', 'usage_events', ['event_type'], unique=False)
    op.create_index('ix_usage_events_created_at', 'usage_events', ['created_at'], unique=False)

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE plans
            SET limite_playlists_privadas = COALESCE(limite_playlists_privadas, 1),
                limite_usuarios = COALESCE(limite_usuarios, 1)
            """
        )
    )


def downgrade():
    op.drop_index('ix_usage_events_created_at', table_name='usage_events')
    op.drop_index('ix_usage_events_event_type', table_name='usage_events')
    op.drop_index('ix_usage_events_user_id', table_name='usage_events')
    op.drop_index('ix_usage_events_tenant_id', table_name='usage_events')
    op.drop_table('usage_events')
