from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.controllers.music_controller import MusicController
from app.controllers.playlist_controller import PlaylistController
from app.controllers.auth_controller import AuthController

api_bp = Blueprint('api', __name__)

# ========== Rotas de Música ==========

@api_bp.route('/musicas', methods=['GET'])
def listar_musicas():
    """API: Lista músicas"""
    termo = request.args.get('q')
    limite = request.args.get('limite', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    resultado = MusicController.buscar_musicas(termo, limite, offset)
    return jsonify(resultado)

@api_bp.route('/musicas/<int:musica_id>', methods=['GET'])
def obter_musica(musica_id):
    """API: Obtém detalhes de música"""
    resultado = MusicController.obter_musica(musica_id)
    return jsonify(resultado)

@api_bp.route('/musicas/populares', methods=['GET'])
def musicas_populares():
    """API: Músicas mais populares"""
    limite = request.args.get('limite', 20, type=int)
    resultado = MusicController.obter_musicas_populares(limite)
    return jsonify(resultado)

@api_bp.route('/musicas/<int:musica_id>/reproduzir', methods=['POST'])
@login_required
def reproduzir_musica(musica_id):
    """API: Registra reprodução de música"""
    resultado = MusicController.registrar_reproducao(musica_id)
    return jsonify(resultado)

# ========== Rotas de Playlist ==========

@api_bp.route('/playlists', methods=['GET', 'POST'])
@login_required
def playlists():
    """API: Lista ou cria playlists"""
    if request.method == 'GET':
        resultado = PlaylistController.obter_playlists_usuario(
            current_user.id, 
            include_musicas=request.args.get('include_musicas') == 'true'
        )
        return jsonify(resultado)
    
    elif request.method == 'POST':
        dados = request.get_json()
        resultado = PlaylistController.criar_playlist(
            current_user.id,
            dados.get('nome'),
            dados.get('descricao'),
            dados.get('publica', False)
        )
        return jsonify(resultado), 201 if resultado['success'] else 400

@api_bp.route('/playlists/<int:playlist_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def playlist_detalhes(playlist_id):
    """API: Obtém, atualiza ou deleta playlist"""
    if request.method == 'GET':
        resultado = PlaylistController.obter_playlist(playlist_id, current_user.id)
        return jsonify(resultado)
    
    elif request.method == 'PUT':
        dados = request.get_json()
        resultado = PlaylistController.atualizar_playlist(
            playlist_id, 
            current_user.id, 
            dados
        )
        return jsonify(resultado)
    
    elif request.method == 'DELETE':
        resultado = PlaylistController.deletar_playlist(playlist_id, current_user.id)
        return jsonify(resultado)

@api_bp.route('/playlists/<int:playlist_id>/musicas/<int:musica_id>', methods=['POST', 'DELETE'])
@login_required
def playlist_musicas(playlist_id, musica_id):
    """API: Adiciona ou remove música da playlist"""
    if request.method == 'POST':
        dados = request.get_json() or {}
        resultado = PlaylistController.adicionar_musica(
            playlist_id,
            current_user.id,
            musica_id,
            dados.get('posicao')
        )
        return jsonify(resultado), 201 if resultado['success'] else 400
    
    elif request.method == 'DELETE':
        resultado = PlaylistController.remover_musica(
            playlist_id,
            current_user.id,
            musica_id
        )
        return jsonify(resultado)

@api_bp.route('/playlists/publicas', methods=['GET'])
def playlists_publicas():
    """API: Lista playlists públicas"""
    limite = request.args.get('limite', 20, type=int)
    resultado = PlaylistController.obter_playlists_publicas(limite)
    return jsonify(resultado)

# ========== Rotas de Usuário ==========

@api_bp.route('/usuario/perfil', methods=['GET', 'PUT'])
@login_required
def usuario_perfil():
    """API: Obtém ou atualiza perfil do usuário"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'usuario': current_user.to_dict()
        })
    
    elif request.method == 'PUT':
        dados = request.get_json()
        resultado = AuthController.atualizar_perfil(current_user, dados)
        return jsonify(resultado)

@api_bp.route('/usuario/favoritos/<int:musica_id>', methods=['POST', 'DELETE'])
@login_required
def gerenciar_favoritos(musica_id):
    """API: Adiciona ou remove música dos favoritos"""
    from app.models import Music
    from app.extensions import db
    
    musica = Music.query.get(musica_id)
    
    if not musica:
        return jsonify({'success': False, 'message': 'Música não encontrada'}), 404
    
    try:
        if request.method == 'POST':
            current_user.add_favorito(musica)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Música adicionada aos favoritos'})
        
        elif request.method == 'DELETE':
            current_user.remove_favorito(musica)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Música removida dos favoritos'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== Tratamento de Erros ==========

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Recurso não encontrado'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500