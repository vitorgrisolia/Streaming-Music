"""008_create_audit_logs

Revision ID: f4e2e599a4a8
Revises: d0f9a6946066
Create Date: 2026-03-18 15:51:33.019841

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4e2e599a4a8'
down_revision = 'd0f9a6946066'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('evento', sa.String(length=80), nullable=False),
        sa.Column('nivel', sa.String(length=20), nullable=False, server_default='INFO'),
        sa.Column('detalhe_json', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('data_evento', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_evento', 'audit_logs', ['evento'], unique=False)
    op.create_index('ix_audit_logs_data_evento', 'audit_logs', ['data_evento'], unique=False)


def downgrade():
    op.drop_index('ix_audit_logs_data_evento', table_name='audit_logs')
    op.drop_index('ix_audit_logs_evento', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs')
    op.drop_table('audit_logs')
