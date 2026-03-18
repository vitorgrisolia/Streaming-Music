from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    """Registro de eventos sensiveis para auditoria."""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), index=True)
    evento = db.Column(db.String(80), nullable=False, index=True)
    nivel = db.Column(db.String(20), nullable=False, default='INFO')
    detalhe_json = db.Column(db.Text)
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))
    data_evento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    tenant = db.relationship('Tenant', backref=db.backref('audit_logs', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<AuditLog evento={self.evento} tenant={self.tenant_id}>'
