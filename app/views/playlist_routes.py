from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.controllers.playlist_controller import PlaylistController

playlist_bp = Blueprint('playlist', __name__, url_prefix='/playlist')

@playlist_bp.route('/minhas-playlists')
@login_required
def minhas_playlists():
    """Lista playlists do usuário"""
    resultado = PlaylistController.obter_playlists_usuario(current_user.id)
    
    if resultado['success']:
        playlists = resultado['playlists']
    else:
        playlists = []
        flash(resultado.get('message', 'Erro ao carregar playlists'), 'error')
    
    return render_template('minhas_playlists.html', playlists=playlists)

@playlist_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Cria nova playlist"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        publica = request.form.get('publica') == 'on'
        
        resultado = PlaylistController.criar_playlist(
            current_user.id, 
            nome, 
            descricao, 
            publica
        )
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('playlist.minhas_playlists'))
        else:
            flash(resultado['message'], 'error')
    
    return render_template('criar_playlist.html')

@playlist_bp.route('/<int:playlist_id>')
def detalhes(playlist_id):
    """Detalhes de uma playlist"""
    usuario_id = current_user.id if current_user.is_authenticated else None
    resultado = PlaylistController.obter_playlist(playlist_id, usuario_id)
    
    if not resultado['success']:
        flash(resultado.get('message', 'Playlist não encontrada'), 'error')
        return redirect(url_for('music.index'))
    
    playlist = resultado['playlist']
    is_owner = current_user.is_authenticated and playlist['usuario_id'] == current_user.id
    
    return render_template('playlist_detalhes.html', 
                         playlist=playlist, 
                         is_owner=is_owner)

@playlist_bp.route('/<int:playlist_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(playlist_id):
    """Edita playlist"""
    if request.method == 'POST':
        dados = {
            'nome': request.form.get('nome'),
            'descricao': request.form.get('descricao'),
            'publica': request.form.get('publica') == 'on'
        }
        
        resultado = PlaylistController.atualizar_playlist(
            playlist_id, 
            current_user.id, 
            dados
        )
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('playlist.detalhes', playlist_id=playlist_id))
        else:
            flash(resultado['message'], 'error')
    
    resultado = PlaylistController.obter_playlist(playlist_id, current_user.id)
    
    if not resultado['success']:
        flash(resultado.get('message', 'Playlist não encontrada'), 'error')
        return redirect(url_for('playlist.minhas_playlists'))
    
    playlist = resultado['playlist']
    return render_template('editar_playlist.html', playlist=playlist)

@playlist_bp.route('/<int:playlist_id>/deletar', methods=['POST'])
@login_required
def deletar(playlist_id):
    """Deleta playlist"""
    resultado = PlaylistController.deletar_playlist(playlist_id, current_user.id)
    
    if resultado['success']:
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'error')
    
    return redirect(url_for('playlist.minhas_playlists'))

@playlist_bp.route('/<int:playlist_id>/adicionar-musica/<int:musica_id>', methods=['POST'])
@login_required
def adicionar_musica(playlist_id, musica_id):
    """Adiciona música à playlist"""
    resultado = PlaylistController.adicionar_musica(
        playlist_id, 
        current_user.id, 
        musica_id
    )
    
    if resultado['success']:
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'error')
    
    return redirect(request.referrer or url_for('music.index'))

@playlist_bp.route('/<int:playlist_id>/remover-musica/<int:musica_id>', methods=['POST'])
@login_required
def remover_musica(playlist_id, musica_id):
    """Remove música da playlist"""
    resultado = PlaylistController.remover_musica(
        playlist_id, 
        current_user.id, 
        musica_id
    )
    
    if resultado['success']:
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'error')
    
    return redirect(url_for('playlist.detalhes', playlist_id=playlist_id))

@playlist_bp.route('/publicas')
def publicas():
    """Lista playlists públicas"""
    resultado = PlaylistController.obter_playlists_publicas(limite=50)
    
    if resultado['success']:
        playlists = resultado['playlists']
    else:
        playlists = []
        flash(resultado.get('message', 'Erro ao carregar playlists'), 'error')
    
    return render_template('playlists_publicas.html', playlists=playlists)