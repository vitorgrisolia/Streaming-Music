from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.controllers.music_controller import MusicController
from app.models import Artist, Album

music_bp = Blueprint('music', __name__)

@music_bp.route('/')
def index():
    """Página inicial"""
    resultado = MusicController.obter_musicas_populares(limite=10)
    musicas_populares = resultado.get('musicas', []) if resultado['success'] else []
    
    return render_template('index.html', musicas_populares=musicas_populares)

@music_bp.route('/buscar')
def buscar():
    """Busca de músicas"""
    termo = request.args.get('q', '')
    pagina = request.args.get('pagina', 1, type=int)
    limite = 20
    offset = (pagina - 1) * limite
    
    resultado = MusicController.buscar_musicas(termo, limite, offset)
    
    if resultado['success']:
        musicas = resultado['musicas']
        total = resultado['total']
        total_paginas = (total + limite - 1) // limite
    else:
        musicas = []
        total = 0
        total_paginas = 0
        flash(resultado.get('message', 'Erro ao buscar músicas'), 'error')
    
    return render_template('buscar.html', 
                         musicas=musicas,
                         termo=termo,
                         pagina=pagina,
                         total_paginas=total_paginas,
                         total=total)

@music_bp.route('/musica/<int:musica_id>')
def musica_detalhes(musica_id):
    """Detalhes de uma música"""
    resultado = MusicController.obter_musica(musica_id)
    
    if not resultado['success']:
        flash(resultado.get('message', 'Música não encontrada'), 'error')
        return redirect(url_for('music.index'))
    
    musica = resultado['musica']
    return render_template('musica_detalhes.html', musica=musica)

@music_bp.route('/artista/<int:artista_id>')
def artista_detalhes(artista_id):
    """Detalhes de um artista"""
    artista = Artist.query.get_or_404(artista_id)
    albuns = artista.albuns.all()
    
    return render_template('artista_detalhes.html', artista=artista, albuns=albuns)

@music_bp.route('/album/<int:album_id>')
def album_detalhes(album_id):
    """Detalhes de um álbum"""
    album = Album.query.get_or_404(album_id)
    musicas = album.musicas.order_by('numero_faixa').all()
    
    return render_template('album_detalhes.html', album=album, musicas=musicas)

@music_bp.route('/player')
@login_required
def player():
    """Player de música"""
    musica_id = request.args.get('id', type=int)
    
    if not musica_id:
        flash('Música não especificada', 'error')
        return redirect(url_for('music.index'))
    
    resultado = MusicController.obter_musica(musica_id)
    
    if not resultado['success']:
        flash(resultado.get('message', 'Música não encontrada'), 'error')
        return redirect(url_for('music.index'))
    
    # Registra reprodução
    MusicController.registrar_reproducao(musica_id)
    
    musica = resultado['musica']
    return render_template('player.html', musica=musica)