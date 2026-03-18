from datetime import datetime

from app.extensions import db


class UsageEvent(db.Model):
    """Evento de uso para controle de limites de plano."""

    __tablename__ = 'usage_events'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), index=True)
    event_type = db.Column(db.String(80), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    metadata_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    tenant = db.relationship('Tenant', backref=db.backref('usage_events', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('usage_events', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'quantity': self.quantity,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<UsageEvent tenant={self.tenant_id} event={self.event_type}>'
