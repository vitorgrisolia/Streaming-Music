from datetime import datetime

from app.extensions import db


class Subscription(db.Model):
    """Assinatura ativa de um tenant."""

    __tablename__ = 'subscriptions'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', name='uq_subscriptions_tenant'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default='inactive')
    stripe_customer_id = db.Column(db.String(120), index=True)
    stripe_subscription_id = db.Column(db.String(120), unique=True, index=True)
    periodo_inicio = db.Column(db.DateTime)
    periodo_fim = db.Column(db.DateTime)
    cancel_at_period_end = db.Column(db.Boolean, nullable=False, default=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship('Tenant', backref=db.backref('subscription_rel', uselist=False))
    plan = db.relationship('Plan', backref=db.backref('subscriptions', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'stripe_customer_id': self.stripe_customer_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fim': self.periodo_fim.isoformat() if self.periodo_fim else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'data_criacao': self.data_criacao.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat(),
            'plan': self.plan.to_dict() if self.plan else None,
        }

    def __repr__(self):
        return f'<Subscription tenant={self.tenant_id} status={self.status}>'
