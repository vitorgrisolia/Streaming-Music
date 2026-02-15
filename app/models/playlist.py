from datetime import datetime
from app.extensions import db

class Playlist(db.Model):
    """Model de Playlist"""
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    publica = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    musicas = db.relationship('Music', secondary='playlist_musicas', backref='playlists', lazy='dynamic')
    
    def __init__(self, usuario_id, nome, descricao=None, publica=False):
        self.usuario_id = usuario_id
        self.nome = nome
        self.descricao = descricao
        self.publica = publica
    
    def adicionar_musica(self, musica, posicao=None):
        """Adiciona uma música à playlist"""
        if not self.tem_musica(musica):
            if posicao is None:
                posicao = self.musicas.count() + 1
            
            playlist_musica = PlaylistMusica(
                playlist_id=self.id,
                musica_id=musica.id,
                posicao=posicao
            )
            db.session.add(playlist_musica)
            return True
        return False
    
    def remover_musica(self, musica):
        """Remove uma música da playlist"""
        if self.tem_musica(musica):
            PlaylistMusica.query.filter_by(
                playlist_id=self.id,
                musica_id=musica.id
            ).delete()
            return True
        return False
    
    def tem_musica(self, musica):
        """Verifica se música está na playlist"""
        return self.musicas.filter_by(id=musica.id).count() > 0
    
    @property
    def total_musicas(self):
        """Retorna total de músicas da playlist"""
        return self.musicas.count()
    
    @property
    def duracao_total(self):
        """Retorna duração total da playlist em segundos"""
        return sum(musica.duracao for musica in self.musicas if musica.duracao)
    
    def to_dict(self, include_musicas=False):
        """Retorna representação em dicionário"""
        data = {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'data_criacao': self.data_criacao.isoformat(),
            'publica': self.publica,
            'total_musicas': self.total_musicas,
            'duracao_total': self.duracao_total
        }
        
        if include_musicas:
            musicas_ordenadas = PlaylistMusica.query.filter_by(
                playlist_id=self.id
            ).order_by(PlaylistMusica.posicao).all()
            
            data['musicas'] = [
                {**pm.musica.to_dict(), 'posicao': pm.posicao}
                for pm in musicas_ordenadas
            ]
        
        return data
    
    def __repr__(self):
        return f'<Playlist {self.nome}>'


class PlaylistMusica(db.Model):
    """Tabela associativa entre Playlist e Music"""
    __tablename__ = 'playlist_musicas'
    
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    musica_id = db.Column(db.Integer, db.ForeignKey('musicas.id'), nullable=False)
    posicao = db.Column(db.Integer, default=1)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos explícitos
    playlist = db.relationship('Playlist', backref='playlist_musicas_rel')
    musica = db.relationship('Music', backref='playlist_musicas_rel')
    
    def __repr__(self):
        return f'<PlaylistMusica playlist_id={self.playlist_id} musica_id={self.musica_id}>'