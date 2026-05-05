"""005_create_subscriptions

Revision ID: c680ff7bb836
Revises: de6edac4518f
Create Date: 2026-03-18 15:51:13.653159

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

UTC = timezone.utc


# revision identifiers, used by Alembic.
revision = 'c680ff7bb836'
down_revision = 'de6edac4518f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='inactive'),
        sa.Column('stripe_customer_id', sa.String(length=120), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=120), nullable=True),
        sa.Column('periodo_inicio', sa.DateTime(), nullable=True),
        sa.Column('periodo_fim', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', name='uq_subscriptions_tenant'),
    )
    op.create_index('ix_subscriptions_tenant_id', 'subscriptions', ['tenant_id'], unique=False)
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'], unique=False)
    op.create_index('ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'], unique=False)
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)

    connection = op.get_bind()
    free_plan_id = connection.execute(
        sa.text("SELECT id FROM plans WHERE codigo = 'free' ORDER BY id LIMIT 1")
    ).scalar()
    if free_plan_id is not None:
        now = datetime.now(UTC)
        connection.execute(
            sa.text(
                """
                INSERT INTO subscriptions
                (tenant_id, plan_id, status, cancel_at_period_end, data_criacao, atualizado_em)
                SELECT t.id, :plan_id, :status, :cancel, :data, :data
                FROM tenants t
                WHERE NOT EXISTS (
                    SELECT 1 FROM subscriptions s WHERE s.tenant_id = t.id
                )
                """
            ),
            {
                'plan_id': int(free_plan_id),
                'status': 'active',
                'cancel': False,
                'data': now,
            },
        )


def downgrade():
    op.drop_index('ix_subscriptions_stripe_subscription_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_stripe_customer_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_plan_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_tenant_id', table_name='subscriptions')
    op.drop_table('subscriptions')
