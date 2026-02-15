from app.models.user import User, favoritos
from app.models.artist import Artist
from app.models.album import Album
from app.models.music import Music
from app.models.playlist import Playlist, PlaylistMusica

__all__ = [
    'User',
    'Artist',
    'Album',
    'Music',
    'Playlist',
    'PlaylistMusica',
    'favoritos'
]