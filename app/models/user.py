from datetime import datetime

from flask_login import UserMixin

from app.extensions import bcrypt, db


class User(UserMixin, db.Model):
    """Model de usuario."""

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    email_verificado_em = db.Column(db.DateTime)
    email_verificacao_token = db.Column(db.String(255), unique=True, index=True)
    reset_senha_token = db.Column(db.String(255), unique=True, index=True)
    reset_senha_expira_em = db.Column(db.DateTime)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    playlists = db.relationship('Playlist', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    favoritos = db.relationship('Music', secondary='favoritos', backref='usuarios_favoritaram', lazy='dynamic')
    memberships = db.relationship(
        'Membership',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )

    def __init__(
        self,
        nome,
        email,
        senha,
        tenant_id=None,
        email_verificado_em=None,
        email_verificacao_token=None,
        reset_senha_token=None,
        reset_senha_expira_em=None,
    ):
        self.tenant_id = tenant_id
        self.nome = nome
        self.email = email
        self.email_verificado_em = email_verificado_em
        self.email_verificacao_token = email_verificacao_token
        self.reset_senha_token = reset_senha_token
        self.reset_senha_expira_em = reset_senha_expira_em
        self.set_password(senha)

    def set_password(self, senha):
        """Criptografa e define a senha do usuario."""
        senha_criptografada = bcrypt.generate_password_hash(senha)

        if isinstance(senha_criptografada, bytes):
            try:
                self.senha = senha_criptografada.decode('utf-8')
            except UnicodeDecodeError:
                self.senha = senha_criptografada.decode('latin-1')
            return

        self.senha = senha_criptografada

    def check_password(self, senha):
        """Verifica se a senha esta correta."""
        return bcrypt.check_password_hash(self.senha, senha)

    @property
    def email_verificado(self):
        return self.email_verificado_em is not None

    def add_favorito(self, musica):
        """Adiciona musica aos favoritos."""
        if not self.is_favorito(musica):
            self.favoritos.append(musica)

    def remove_favorito(self, musica):
        """Remove musica dos favoritos."""
        if self.is_favorito(musica):
            self.favoritos.remove(musica)

    def is_favorito(self, musica):
        """Verifica se musica esta nos favoritos."""
        return self.favoritos.filter_by(id=musica.id).count() > 0

    def to_dict(self):
        """Retorna representacao em dicionario."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'nome': self.nome,
            'email': self.email,
            'email_verificado': self.email_verificado,
            'email_verificado_em': self.email_verificado_em.isoformat() if self.email_verificado_em else None,
            'data_criacao': self.data_criacao.isoformat(),
            'total_playlists': self.playlists.count(),
            'total_favoritos': self.favoritos.count(),
        }

    def __repr__(self):
        return f'<User {self.email}>'


favoritos = db.Table(
    'favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('musica_id', db.Integer, db.ForeignKey('musicas.id'), primary_key=True),
    db.Column('data_adicao', db.DateTime, default=datetime.utcnow),
)
