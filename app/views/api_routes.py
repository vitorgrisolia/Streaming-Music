from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.controllers.auth_controller import AuthController
from app.controllers.billing_controller import BillingController
from app.controllers.music_controller import MusicController
from app.controllers.playlist_controller import PlaylistController

api_bp = Blueprint('api', __name__)


@api_bp.route('/musicas', methods=['GET'])
def listar_musicas():
    """API: lista musicas."""
    termo = request.args.get('q')
    limite = max(request.args.get('limite', 50, type=int) or 50, 1)
    offset = max(request.args.get('offset', 0, type=int) or 0, 0)

    resultado = MusicController.buscar_musicas(termo, limite, offset)
    return jsonify(resultado)


@api_bp.route('/musicas/<int:musica_id>', methods=['GET'])
def obter_musica(musica_id):
    """API: obtem detalhes de musica."""
    resultado = MusicController.obter_musica(musica_id)
    return jsonify(resultado)


@api_bp.route('/musicas/populares', methods=['GET'])
def musicas_populares():
    """API: musicas mais populares."""
    limite = max(request.args.get('limite', 20, type=int) or 20, 1)
    resultado = MusicController.obter_musicas_populares(limite)
    return jsonify(resultado)


@api_bp.route('/musicas/<int:musica_id>/reproduzir', methods=['POST'])
@login_required
def reproduzir_musica(musica_id):
    """API: registra reproducao de musica."""
    resultado = MusicController.registrar_reproducao(musica_id)
    return jsonify(resultado)


@api_bp.route('/playlists', methods=['GET', 'POST'])
@login_required
def playlists():
    """API: lista ou cria playlists."""
    if request.method == 'GET':
        resultado = PlaylistController.obter_playlists_usuario(
            current_user.id,
            include_musicas=request.args.get('include_musicas') == 'true',
        )
        return jsonify(resultado)

    dados = request.get_json(silent=True) or {}
    if not dados.get('nome'):
        return jsonify({'success': False, 'message': 'Campo nome e obrigatorio'}), 400

    resultado = PlaylistController.criar_playlist(
        current_user.id,
        dados.get('nome'),
        dados.get('descricao'),
        dados.get('publica', False),
    )
    return jsonify(resultado), 201 if resultado['success'] else 400


@api_bp.route('/playlists/<int:playlist_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def playlist_detalhes(playlist_id):
    """API: obtem, atualiza ou deleta playlist."""
    if request.method == 'GET':
        resultado = PlaylistController.obter_playlist(
            playlist_id,
            current_user.id,
            tenant_id=current_user.tenant_id,
        )
        return jsonify(resultado)

    if request.method == 'PUT':
        dados = request.get_json(silent=True) or {}
        resultado = PlaylistController.atualizar_playlist(playlist_id, current_user.id, dados)
        return jsonify(resultado)

    resultado = PlaylistController.deletar_playlist(playlist_id, current_user.id)
    return jsonify(resultado)


@api_bp.route('/playlists/<int:playlist_id>/musicas/<int:musica_id>', methods=['POST', 'DELETE'])
@login_required
def playlist_musicas(playlist_id, musica_id):
    """API: adiciona ou remove musica da playlist."""
    if request.method == 'POST':
        dados = request.get_json(silent=True) or {}
        resultado = PlaylistController.adicionar_musica(
            playlist_id,
            current_user.id,
            musica_id,
            dados.get('posicao'),
        )
        return jsonify(resultado), 201 if resultado['success'] else 400

    resultado = PlaylistController.remover_musica(playlist_id, current_user.id, musica_id)
    return jsonify(resultado)


@api_bp.route('/playlists/publicas', methods=['GET'])
def playlists_publicas():
    """API: lista playlists publicas do tenant corrente."""
    limite = request.args.get('limite', 20, type=int)
    tenant_id = current_user.tenant_id if current_user.is_authenticated else None
    resultado = PlaylistController.obter_playlists_publicas(limite, tenant_id=tenant_id)
    return jsonify(resultado)


@api_bp.route('/billing/plans', methods=['GET'])
def billing_plans():
    """API: retorna planos ativos."""
    resultado = BillingController.listar_planos()
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/billing/subscription', methods=['GET'])
@login_required
def billing_subscription():
    """API: retorna assinatura do tenant do usuario logado."""
    resultado = BillingController.obter_assinatura_tenant(current_user.tenant_id)
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/billing/checkout', methods=['POST'])
@login_required
def billing_checkout():
    """API: inicia checkout Stripe para troca/contratacao de plano."""
    dados = request.get_json(silent=True) or {}
    plan_code = dados.get('plan_code')
    success_url = dados.get('success_url')
    cancel_url = dados.get('cancel_url')

    if not plan_code or not success_url or not cancel_url:
        return jsonify({'success': False, 'message': 'plan_code, success_url e cancel_url sao obrigatorios'}), 400

    resultado = BillingController.iniciar_checkout(
        tenant_id=current_user.tenant_id,
        customer_email=current_user.email,
        plan_code=plan_code,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/billing/portal', methods=['POST'])
@login_required
def billing_portal():
    """API: abre portal de faturamento Stripe."""
    dados = request.get_json(silent=True) or {}
    return_url = dados.get('return_url')
    if not return_url:
        return jsonify({'success': False, 'message': 'return_url e obrigatorio'}), 400

    resultado = BillingController.criar_portal_cobranca(
        tenant_id=current_user.tenant_id,
        return_url=return_url,
    )
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/billing/webhook', methods=['POST'])
def billing_webhook():
    """API: endpoint de webhook Stripe."""
    raw_payload = request.get_data(as_text=True)
    stripe_signature = request.headers.get('Stripe-Signature')
    resultado = BillingController.processar_webhook(raw_payload, stripe_signature)
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/auth/verificar-email', methods=['POST'])
def auth_verificar_email():
    """API: confirma verificacao de email por token."""
    dados = request.get_json(silent=True) or {}
    resultado = AuthController.verificar_email_token(dados.get('token'))
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/auth/solicitar-reset', methods=['POST'])
def auth_solicitar_reset():
    """API: solicita reset de senha."""
    dados = request.get_json(silent=True) or {}
    resultado = AuthController.solicitar_reset_senha(dados.get('email'))
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/auth/redefinir-senha', methods=['POST'])
def auth_redefinir_senha():
    """API: redefine senha com token."""
    dados = request.get_json(silent=True) or {}
    resultado = AuthController.redefinir_senha(
        token=dados.get('token'),
        nova_senha=dados.get('nova_senha'),
    )
    return jsonify(resultado), 200 if resultado.get('success') else 400


@api_bp.route('/usuario/perfil', methods=['GET', 'PUT'])
@login_required
def usuario_perfil():
    """API: obtem ou atualiza perfil do usuario."""
    if request.method == 'GET':
        return jsonify({'success': True, 'usuario': current_user.to_dict()})

    dados = request.get_json(silent=True) or {}
    resultado = AuthController.atualizar_perfil(current_user, dados)
    return jsonify(resultado)


@api_bp.route('/usuario/favoritos/<int:musica_id>', methods=['POST', 'DELETE'])
@login_required
def gerenciar_favoritos(musica_id):
    """API: adiciona ou remove musica dos favoritos."""
    from app.extensions import db
    from app.models import Music

    musica = db.session.get(Music, musica_id)
    if not musica:
        return jsonify({'success': False, 'message': 'Musica nao encontrada'}), 404

    try:
        if request.method == 'POST':
            current_user.add_favorito(musica)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Musica adicionada aos favoritos'})

        current_user.remove_favorito(musica)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Musica removida dos favoritos'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Recurso nao encontrado'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
