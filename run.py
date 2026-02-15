import os
from app import create_app
from app.extensions import db
from app.models import User, Artist, Album, Music, Playlist

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Contexto para shell interativo"""
    return {
        'db': db,
        'User': User,
        'Artist': Artist,
        'Album': Album,
        'Music': Music,
        'Playlist': Playlist
    }

@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado!')

@app.cli.command()
def seed_db():
    """Popula banco com dados de exemplo"""
    from datetime import datetime
    
    # Limpa dados existentes
    db.drop_all()
    db.create_all()
    
    # Cria usuário de teste
    usuario = User(
        nome='Usuário Teste',
        email='teste@email.com',
        senha='senha123'
    )
    db.session.add(usuario)
    
    # Cria artistas
    artista1 = Artist(
        nome='The Beatles',
        genero='Rock',
        bio='Banda britânica de rock formada em Liverpool em 1960'
    )
    
    artista2 = Artist(
        nome='Pink Floyd',
        genero='Rock Progressivo',
        bio='Banda britânica de rock progressivo'
    )
    
    db.session.add_all([artista1, artista2])
    db.session.commit()
    
    # Cria álbuns
    album1 = Album(
        titulo='Abbey Road',
        artista_id=artista1.id,
        ano_lancamento=1969
    )
    
    album2 = Album(
        titulo='The Dark Side of the Moon',
        artista_id=artista2.id,
        ano_lancamento=1973
    )
    
    db.session.add_all([album1, album2])
    db.session.commit()
    
    # Cria músicas
    musicas = [
        Music(titulo='Come Together', album_id=album1.id, 
            arquivo_url='/static/music/come-together.mp3', duracao=259, numero_faixa=1),
        Music(titulo='Something', album_id=album1.id,
            arquivo_url='/static/music/something.mp3', duracao=182, numero_faixa=2),
        Music(titulo='Time', album_id=album2.id,
            arquivo_url='/static/music/time.mp3', duracao=413, numero_faixa=1),
        Music(titulo='Money', album_id=album2.id,
            arquivo_url='/static/music/money.mp3', duracao=382, numero_faixa=2),
    ]
    
    db.session.add_all(musicas)
    db.session.commit()
    
    # Cria playlist
    playlist = Playlist(
        usuario_id=usuario.id,
        nome='Minhas Favoritas',
        descricao='Playlist com músicas clássicas',
        publica=True
    )
    db.session.add(playlist)
    db.session.commit()
    
    # Adiciona músicas à playlist
    playlist.adicionar_musica(musicas[0], 1)
    playlist.adicionar_musica(musicas[2], 2)
    db.session.commit()
    
    print('Banco de dados populado com dados de exemplo!')
    print(f'Usuário: teste@email.com / senha123')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)