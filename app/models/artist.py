from app.extensions import db

class Artist(db.Model):
    """Model de Artista"""
    __tablename__ = 'artistas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    genero = db.Column(db.String(50))
    bio = db.Column(db.Text)
    imagem_url = db.Column(db.String(255))
    
    # Relacionamentos
    albuns = db.relationship('Album', backref='artista', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, nome, genero=None, bio=None, imagem_url=None):
        self.nome = nome
        self.genero = genero
        self.bio = bio
        self.imagem_url = imagem_url
    
    @property
    def total_albuns(self):
        """Retorna total de álbuns do artista"""
        return self.albuns.count()
    
    @property
    def total_musicas(self):
        """Retorna total de músicas do artista"""
        from app.models.music import Music
        return Music.query.join(Album).filter(Album.artista_id == self.id).count()
    
    def to_dict(self):
        """Retorna representação em dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'genero': self.genero,
            'bio': self.bio,
            'imagem_url': self.imagem_url,
            'total_albuns': self.total_albuns,
            'total_musicas': self.total_musicas
        }
    
    def __repr__(self):
        return f'<Artist {self.nome}>'