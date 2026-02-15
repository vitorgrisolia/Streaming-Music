from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    """Model de Usuário"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    playlists = db.relationship('Playlist', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    favoritos = db.relationship('Music', secondary='favoritos', backref='usuarios_favoritaram', lazy='dynamic')
    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.set_password(senha)
    
    def set_password(self, senha):
        """Criptografa e define a senha do usuário"""
        self.senha = bcrypt.generate_password_hash(senha).decode('utf-8')
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return bcrypt.check_password_hash(self.senha, senha)
    
    def add_favorito(self, musica):
        """Adiciona música aos favoritos"""
        if not self.is_favorito(musica):
            self.favoritos.append(musica)
    
    def remove_favorito(self, musica):
        """Remove música dos favoritos"""
        if self.is_favorito(musica):
            self.favoritos.remove(musica)
    
    def is_favorito(self, musica):
        """Verifica se música está nos favoritos"""
        return self.favoritos.filter_by(id=musica.id).count() > 0
    
    def to_dict(self):
        """Retorna representação em dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'data_criacao': self.data_criacao.isoformat(),
            'total_playlists': self.playlists.count(),
            'total_favoritos': self.favoritos.count()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


# Tabela associativa para favoritos
favoritos = db.Table('favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('musica_id', db.Integer, db.ForeignKey('musicas.id'), primary_key=True),
    db.Column('data_adicao', db.DateTime, default=datetime.utcnow)
)