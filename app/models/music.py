from app.extensions import db

class Music(db.Model):
    """Model de Música"""
    __tablename__ = 'musicas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False, index=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albuns.id'), nullable=False)
    duracao = db.Column(db.Integer)  # em segundos
    arquivo_url = db.Column(db.String(255), nullable=False)
    numero_faixa = db.Column(db.Integer)
    visualizacoes = db.Column(db.Integer, default=0)
    
    def __init__(self, titulo, album_id, arquivo_url, duracao=None, numero_faixa=None):
        self.titulo = titulo
        self.album_id = album_id
        self.arquivo_url = arquivo_url
        self.duracao = duracao
        self.numero_faixa = numero_faixa
    
    def incrementar_visualizacao(self):
        """Incrementa contador de visualizações"""
        self.visualizacoes += 1
        db.session.commit()
    
    @property
    def duracao_formatada(self):
        """Retorna duração formatada (MM:SS)"""
        if not self.duracao:
            return "00:00"
        minutos = self.duracao // 60
        segundos = self.duracao % 60
        return f"{minutos:02d}:{segundos:02d}"
    
    def to_dict(self, include_album=True):
        """Retorna representação em dicionário"""
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'album_id': self.album_id,
            'duracao': self.duracao,
            'duracao_formatada': self.duracao_formatada,
            'arquivo_url': self.arquivo_url,
            'numero_faixa': self.numero_faixa,
            'visualizacoes': self.visualizacoes
        }
        
        if include_album and self.album:
            data['album'] = {
                'id': self.album.id,
                'titulo': self.album.titulo,
                'capa_url': self.album.capa_url,
                'artista': {
                    'id': self.album.artista.id,
                    'nome': self.album.artista.nome
                } if self.album.artista else None
            }
        
        return data
    
    def __repr__(self):
        return f'<Music {self.titulo}>'