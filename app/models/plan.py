from datetime import datetime

from app.extensions import db


class Plan(db.Model):
    """Plano comercial do SaaS."""

    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco_mensal_centavos = db.Column(db.Integer, nullable=False, default=0)
    moeda = db.Column(db.String(8), nullable=False, default='brl')
    stripe_price_id = db.Column(db.String(120), unique=True, index=True)
    limite_playlists_privadas = db.Column(db.Integer, nullable=False, default=1)
    limite_usuarios = db.Column(db.Integer, nullable=False, default=1)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco_mensal_centavos': self.preco_mensal_centavos,
            'moeda': self.moeda,
            'stripe_price_id': self.stripe_price_id,
            'limite_playlists_privadas': self.limite_playlists_privadas,
            'limite_usuarios': self.limite_usuarios,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat(),
        }

    def __repr__(self):
        return f'<Plan {self.codigo}>'
