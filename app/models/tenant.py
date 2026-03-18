from datetime import datetime

from flask import current_app, has_app_context

from app.extensions import db


class Tenant(db.Model):
    """Workspace/empresa dona dos dados da aplicacao."""

    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), nullable=False, unique=True, index=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usuarios = db.relationship('User', backref='tenant', lazy='dynamic')
    playlists = db.relationship('Playlist', backref='tenant', lazy='dynamic')
    memberships = db.relationship(
        'Membership',
        back_populates='tenant',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )

    @staticmethod
    def default_slug():
        """Slug padrao usado quando ainda nao existe resolucao por subdominio."""
        configured = current_app.config.get('DEFAULT_TENANT_SLUG') if has_app_context() else None
        return (configured or 'default').strip().lower()

    @classmethod
    def resolve_default(cls):
        """Retorna o tenant default do sistema."""
        tenant = cls.query.filter_by(slug=cls.default_slug()).first()
        if tenant:
            return tenant
        return cls.query.order_by(cls.id.asc()).first()

    @classmethod
    def resolve_default_id(cls):
        tenant = cls.resolve_default()
        return tenant.id if tenant else None

    def __repr__(self):
        return f'<Tenant {self.slug}>'
