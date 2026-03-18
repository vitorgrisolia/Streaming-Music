import hashlib
import secrets
from datetime import datetime

from app.extensions import db


class ApiKey(db.Model):
    """Chave de API para integracoes externas do tenant."""

    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), index=True)
    nome = db.Column(db.String(80), nullable=False)
    chave_hash = db.Column(db.String(128), nullable=False, unique=True, index=True)
    prefixo = db.Column(db.String(12), nullable=False, index=True)
    ultimo_uso_em = db.Column(db.DateTime)
    expira_em = db.Column(db.DateTime)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    tenant = db.relationship('Tenant', backref=db.backref('api_keys', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('api_keys', lazy='dynamic'))

    @staticmethod
    def hash_raw_key(raw_key):
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    @classmethod
    def generate_raw_key(cls):
        return f"smk_{secrets.token_urlsafe(32)}"

    @classmethod
    def create_with_raw_key(cls, tenant_id, nome, user_id=None, expira_em=None):
        raw_key = cls.generate_raw_key()
        api_key = cls(
            tenant_id=tenant_id,
            user_id=user_id,
            nome=nome,
            chave_hash=cls.hash_raw_key(raw_key),
            prefixo=raw_key[:12],
            expira_em=expira_em,
            ativo=True,
        )
        return api_key, raw_key

    def __repr__(self):
        return f'<ApiKey tenant={self.tenant_id} nome={self.nome}>'
