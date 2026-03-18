"""007_add_email_verification_fields

Revision ID: d0f9a6946066
Revises: 4c91b33b49cb
Create Date: 2026-03-18 15:51:26.171017

"""
from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0f9a6946066'
down_revision = '4c91b33b49cb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verificado_em', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('email_verificacao_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('reset_senha_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('reset_senha_expira_em', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_usuarios_email_verificacao_token', ['email_verificacao_token'], unique=True)
        batch_op.create_index('ix_usuarios_reset_senha_token', ['reset_senha_token'], unique=True)

    connection = op.get_bind()
    connection.execute(
        sa.text('UPDATE usuarios SET email_verificado_em = :agora WHERE email_verificado_em IS NULL'),
        {'agora': datetime.now(UTC)},
    )


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_index('ix_usuarios_reset_senha_token')
        batch_op.drop_index('ix_usuarios_email_verificacao_token')
        batch_op.drop_column('reset_senha_expira_em')
        batch_op.drop_column('reset_senha_token')
        batch_op.drop_column('email_verificacao_token')
        batch_op.drop_column('email_verificado_em')
