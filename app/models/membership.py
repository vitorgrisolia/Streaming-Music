from datetime import datetime

from app.extensions import db


class Membership(db.Model):
    """Relaciona usuario e tenant, permitindo papeis por workspace."""

    __tablename__ = 'tenant_memberships'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'user_id', name='uq_tenant_membership_tenant_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False, default='member')
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    tenant = db.relationship('Tenant', back_populates='memberships')
    user = db.relationship('User', back_populates='memberships')

    def __repr__(self):
        return f'<Membership tenant={self.tenant_id} user={self.user_id} role={self.role}>'
