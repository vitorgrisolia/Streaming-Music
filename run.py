import math
import re
import struct
import unicodedata
import wave
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import User, Artist, Album, Music, Playlist

app = create_app()
SEED_AUDIO_DURATION_SECONDS = 12
SEED_AUDIO_SAMPLE_RATE = 22050
SEED_AUDIO_AMPLITUDE = 0.25


def _slugify(value):
    normalized = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    normalized = normalized.lower()
    normalized = re.sub(r'[^a-z0-9]+', '-', normalized).strip('-')
    return normalized or 'track'


def _build_wav_file(file_path, frequency_hz):
    total_samples = SEED_AUDIO_DURATION_SECONDS * SEED_AUDIO_SAMPLE_RATE
    fade_samples = int(SEED_AUDIO_SAMPLE_RATE * 0.05)
    amplitude = int(32767 * SEED_AUDIO_AMPLITUDE)

    frames = bytearray()
    for sample_index in range(total_samples):
        sample = math.sin(2 * math.pi * frequency_hz * (sample_index / SEED_AUDIO_SAMPLE_RATE))

        # Pequeno fade in/out para evitar clique no inicio/fim do arquivo.
        envelope = 1.0
        if sample_index < fade_samples:
            envelope = sample_index / max(fade_samples, 1)
        elif sample_index > (total_samples - fade_samples):
            envelope = max((total_samples - sample_index) / max(fade_samples, 1), 0.0)

        value = int(sample * envelope * amplitude)
        frames.extend(struct.pack('<h', value))

    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SEED_AUDIO_SAMPLE_RATE)
        wav_file.writeframes(bytes(frames))


def _ensure_seed_audio(file_path, frequency_hz):
    if file_path.exists():
        return
    _build_wav_file(file_path, frequency_hz)


def _build_seed_catalog():
    return [
        {
            'artist': {
                'nome': 'Aurora Pulse',
                'genero': 'Synthwave',
                'bio': 'Projeto eletronico com atmosferas noturnas e linhas melodicas.'
            },
            'album': {
                'titulo': 'Neon Nights',
                'ano_lancamento': 2024,
                'descricao': 'Colecao inspirada em viagens noturnas pela cidade.'
            },
            'tracks': [
                {'titulo': 'City Lights', 'freq': 261.63},
                {'titulo': 'Midnight Drive', 'freq': 293.66},
                {'titulo': 'Skyline Dreams', 'freq': 329.63},
                {'titulo': 'Afterglow', 'freq': 349.23},
            ]
        },
        {
            'artist': {
                'nome': 'Serra Azul Trio',
                'genero': 'MPB Jazz',
                'bio': 'Trio instrumental com foco em arranjos leves e melodicos.'
            },
            'album': {
                'titulo': 'Cafe de Esquina',
                'ano_lancamento': 2022,
                'descricao': 'Faixas tranquilas para ouvir sem pressa.'
            },
            'tracks': [
                {'titulo': 'Manha de Domingo', 'freq': 220.00},
                {'titulo': 'Rua sem Pressa', 'freq': 246.94},
                {'titulo': 'Janela Aberta', 'freq': 277.18},
                {'titulo': 'Chuva no Telhado', 'freq': 311.13},
            ]
        },
        {
            'artist': {
                'nome': 'Lumen Rock',
                'genero': 'Alternative Rock',
                'bio': 'Banda alternativa com riffs marcantes e refrains energicos.'
            },
            'album': {
                'titulo': 'Fase Lunar',
                'ano_lancamento': 2023,
                'descricao': 'Album conceitual sobre ciclos, energia e espaco.'
            },
            'tracks': [
                {'titulo': 'Eclipse Parcial', 'freq': 369.99},
                {'titulo': 'Gravidade Zero', 'freq': 392.00},
                {'titulo': 'Mar de Marte', 'freq': 415.30},
                {'titulo': 'Orbitas', 'freq': 440.00},
            ]
        },
        {
            'artist': {
                'nome': 'Brisa Norte',
                'genero': 'Indie Pop',
                'bio': 'Projeto indie pop com producao luminosa e letras otimistas.'
            },
            'album': {
                'titulo': 'Cartoes Postais',
                'ano_lancamento': 2021,
                'descricao': 'Colecao leve para ouvir em qualquer horario.'
            },
            'tracks': [
                {'titulo': 'Horizonte', 'freq': 466.16},
                {'titulo': 'Vento Bom', 'freq': 493.88},
                {'titulo': 'Setembro', 'freq': 523.25},
                {'titulo': 'Cor de Sol', 'freq': 554.37},
            ]
        },
        {
            'artist': {
                'nome': 'Binary Beats',
                'genero': 'LoFi Electronic',
                'bio': 'Duo eletronico com timbres suaves para foco e relaxamento.'
            },
            'album': {
                'titulo': 'Loop Infinito',
                'ano_lancamento': 2025,
                'descricao': 'Trilhas de fundo para estudo, trabalho e concentracao.'
            },
            'tracks': [
                {'titulo': 'Codigo Aberto', 'freq': 587.33},
                {'titulo': 'Noite de Deploy', 'freq': 622.25},
                {'titulo': 'Build Final', 'freq': 659.25},
                {'titulo': 'Commit do Coracao', 'freq': 698.46},
            ]
        },
    ]


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
    """Popula banco com dados completos para todas as telas (20 musicas)."""

    music_dir = Path(app.root_path) / 'static' / 'music'
    music_dir.mkdir(parents=True, exist_ok=True)

    catalog = _build_seed_catalog()

    # Limpa dados existentes
    db.drop_all()
    db.create_all()

    usuarios = [
        User(nome='Usuario Demo', email='demo@streamingmusic.local', senha='123456'),
        User(nome='Curador Publico', email='curador@streamingmusic.local', senha='123456'),
    ]
    db.session.add_all(usuarios)
    db.session.commit()

    musicas = []
    for catalog_item in catalog:
        artista_info = catalog_item['artist']
        album_info = catalog_item['album']
        track_info = catalog_item['tracks']

        artista = Artist(
            nome=artista_info['nome'],
            genero=artista_info['genero'],
            bio=artista_info['bio']
        )
        db.session.add(artista)
        db.session.flush()

        album = Album(
            titulo=album_info['titulo'],
            artista_id=artista.id,
            ano_lancamento=album_info['ano_lancamento'],
            descricao=album_info['descricao']
        )
        db.session.add(album)
        db.session.flush()

        artist_slug = _slugify(artista.nome)
        album_slug = _slugify(album.titulo)

        for index, track in enumerate(track_info, start=1):
            track_slug = _slugify(track['titulo'])
            file_name = f"{artist_slug}-{album_slug}-{index:02d}-{track_slug}.wav"
            file_path = music_dir / file_name
            _ensure_seed_audio(file_path, track['freq'])

            musica = Music(
                titulo=track['titulo'],
                album_id=album.id,
                arquivo_url=f"/static/music/{file_name}",
                duracao=SEED_AUDIO_DURATION_SECONDS,
                numero_faixa=index
            )
            db.session.add(musica)
            db.session.flush()
            musicas.append(musica)

    # Deixa a tela inicial com ranking consistente de populares.
    for index, musica in enumerate(musicas):
        musica.visualizacoes = 500 - (index * 10)

    # Favoritos para preencher perfil/API de usuario.
    for musica in musicas[:5]:
        usuarios[0].add_favorito(musica)

    playlist_publica = Playlist(
        usuario_id=usuarios[0].id,
        nome='Top 20 do Streaming Music',
        descricao='Playlist completa com as 20 faixas de demonstracao.',
        publica=True
    )
    playlist_privada = Playlist(
        usuario_id=usuarios[0].id,
        nome='Favoritas da Semana',
        descricao='Selecao pessoal para ouvir durante a semana.',
        publica=False
    )
    playlist_curador = Playlist(
        usuario_id=usuarios[1].id,
        nome='Foco no Trabalho',
        descricao='Faixas instrumentais para concentracao.',
        publica=True
    )

    db.session.add_all([playlist_publica, playlist_privada, playlist_curador])
    db.session.commit()

    for position, musica in enumerate(musicas, start=1):
        playlist_publica.adicionar_musica(musica, position)

    for position, musica in enumerate(musicas[:8], start=1):
        playlist_privada.adicionar_musica(musica, position)

    for position, musica in enumerate(musicas[8:18], start=1):
        playlist_curador.adicionar_musica(musica, position)

    db.session.commit()

    print('Seed concluido com sucesso!')
    print(f'Usuarios criados: {User.query.count()}')
    print(f'Artistas criados: {Artist.query.count()}')
    print(f'Albuns criados: {Album.query.count()}')
    print(f'Musicas criadas: {Music.query.count()}')
    print(f'Playlists criadas: {Playlist.query.count()}')
    print(f'Audios em: {music_dir}')
    print('Login demo: demo@streamingmusic.local / 123456')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
