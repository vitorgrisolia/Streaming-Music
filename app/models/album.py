from app.extensions import db

class Album(db.Model):
    """Model de Álbum"""
    __tablename__ = 'albuns'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False, index=True)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
    ano_lancamento = db.Column(db.Integer)
    capa_url = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    
    # Relacionamentos
    musicas = db.relationship('Music', backref='album', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, titulo, artista_id, ano_lancamento=None, capa_url=None, descricao=None):
        self.titulo = titulo
        self.artista_id = artista_id
        self.ano_lancamento = ano_lancamento
        self.capa_url = capa_url
        self.descricao = descricao
    
    @property
    def total_musicas(self):
        """Retorna total de músicas do álbum"""
        return self.musicas.count()
    
    @property
    def duracao_total(self):
        """Retorna duração total do álbum em segundos"""
        return sum(musica.duracao for musica in self.musicas if musica.duracao)
    
    def to_dict(self, include_musicas=False):
        """Retorna representação em dicionário"""
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'artista_id': self.artista_id,
            'artista_nome': self.artista.nome if self.artista else None,
            'ano_lancamento': self.ano_lancamento,
            'capa_url': self.capa_url,
            'descricao': self.descricao,
            'total_musicas': self.total_musicas,
            'duracao_total': self.duracao_total
        }
        
        if include_musicas:
            data['musicas'] = [musica.to_dict() for musica in self.musicas]
        
        return data
    
    def __repr__(self):
        return f'<Album {self.titulo}>'