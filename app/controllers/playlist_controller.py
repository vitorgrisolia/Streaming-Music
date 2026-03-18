from app.extensions import db
from app.models import Music, Playlist, Tenant, User


class PlaylistController:
    """Controller para gerenciamento de playlists."""

    @staticmethod
    def _resolve_tenant_id(usuario_id=None, tenant_id=None):
        if tenant_id is not None:
            return tenant_id
        if usuario_id is not None:
            usuario = db.session.get(User, usuario_id)
            if usuario:
                return usuario.tenant_id
        return Tenant.resolve_default_id()

    @staticmethod
    def _query_playlist_by_tenant(playlist_id, tenant_id):
        query = Playlist.query.filter_by(id=playlist_id)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)
        return query.first()

    @staticmethod
    def criar_playlist(usuario_id, nome, descricao=None, publica=False):
        """Cria nova playlist."""
        try:
            if not nome or len(nome.strip()) < 3:
                return {'success': False, 'message': 'Nome deve ter no minimo 3 caracteres'}

            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            nome_limpo = nome.strip()
            ja_existe = Playlist.query.filter_by(
                tenant_id=usuario.tenant_id,
                usuario_id=usuario_id,
                nome=nome_limpo,
            ).first()
            if ja_existe:
                return {'success': False, 'message': 'Voce ja possui uma playlist com esse nome'}

            if not publica:
                from app.controllers.billing_controller import BillingController

                limite_result = BillingController.can_create_private_playlist(usuario.tenant_id)
                if not limite_result['success']:
                    return {
                        'success': False,
                        'message': (
                            f"{limite_result['message']} "
                            f"({limite_result['used']}/{limite_result['limit']})"
                        ),
                    }

            playlist = Playlist(
                tenant_id=usuario.tenant_id,
                usuario_id=usuario_id,
                nome=nome_limpo,
                descricao=descricao,
                publica=publica,
            )
            db.session.add(playlist)
            db.session.commit()

            from app.controllers.billing_controller import BillingController

            BillingController.registrar_uso(
                tenant_id=usuario.tenant_id,
                user_id=usuario_id,
                event_type='playlist_created',
                quantity=1,
                metadata={'publica': bool(publica), 'playlist_id': playlist.id},
            )

            return {
                'success': True,
                'message': 'Playlist criada com sucesso',
                'playlist': playlist.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao criar playlist: {str(e)}'}

    @staticmethod
    def obter_playlists_usuario(usuario_id, include_musicas=False):
        """Obtem playlists de um usuario dentro do tenant dele."""
        try:
            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            playlists = (
                Playlist.query.filter_by(usuario_id=usuario_id, tenant_id=usuario.tenant_id)
                .order_by(Playlist.data_criacao.desc())
                .all()
            )

            return {
                'success': True,
                'playlists': [p.to_dict(include_musicas=include_musicas) for p in playlists],
            }
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlists: {str(e)}'}

    @staticmethod
    def obter_playlist(playlist_id, usuario_id=None, tenant_id=None):
        """Obtem detalhes de uma playlist respeitando isolamento por tenant."""
        try:
            tenant_resolvido = PlaylistController._resolve_tenant_id(usuario_id=usuario_id, tenant_id=tenant_id)
            playlist = PlaylistController._query_playlist_by_tenant(playlist_id, tenant_resolvido)

            if not playlist:
                return {'success': False, 'message': 'Playlist nao encontrada'}

            if not playlist.publica and playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}

            return {'success': True, 'playlist': playlist.to_dict(include_musicas=True)}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlist: {str(e)}'}

    @staticmethod
    def atualizar_playlist(playlist_id, usuario_id, dados):
        """Atualiza playlist."""
        try:
            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            playlist = PlaylistController._query_playlist_by_tenant(playlist_id, usuario.tenant_id)
            if not playlist:
                return {'success': False, 'message': 'Playlist nao encontrada'}
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}

            if 'nome' in dados and dados['nome']:
                if len(dados['nome'].strip()) < 3:
                    return {'success': False, 'message': 'Nome deve ter no minimo 3 caracteres'}
                playlist.nome = dados['nome'].strip()

            if 'descricao' in dados:
                playlist.descricao = dados['descricao']

            if 'publica' in dados:
                playlist.publica = bool(dados['publica'])

            db.session.commit()
            return {
                'success': True,
                'message': 'Playlist atualizada com sucesso',
                'playlist': playlist.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao atualizar playlist: {str(e)}'}

    @staticmethod
    def deletar_playlist(playlist_id, usuario_id):
        """Deleta playlist."""
        try:
            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            playlist = PlaylistController._query_playlist_by_tenant(playlist_id, usuario.tenant_id)
            if not playlist:
                return {'success': False, 'message': 'Playlist nao encontrada'}
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}

            db.session.delete(playlist)
            db.session.commit()
            return {'success': True, 'message': 'Playlist deletada com sucesso'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao deletar playlist: {str(e)}'}

    @staticmethod
    def adicionar_musica(playlist_id, usuario_id, musica_id, posicao=None):
        """Adiciona musica a playlist."""
        try:
            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            playlist = PlaylistController._query_playlist_by_tenant(playlist_id, usuario.tenant_id)
            if not playlist:
                return {'success': False, 'message': 'Playlist nao encontrada'}
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}

            musica = db.session.get(Music, musica_id)
            if not musica:
                return {'success': False, 'message': 'Musica nao encontrada'}
            if playlist.tem_musica(musica):
                return {'success': False, 'message': 'Musica ja esta na playlist'}

            playlist.adicionar_musica(musica, posicao)
            db.session.commit()
            return {
                'success': True,
                'message': 'Musica adicionada a playlist',
                'playlist': playlist.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao adicionar musica: {str(e)}'}

    @staticmethod
    def remover_musica(playlist_id, usuario_id, musica_id):
        """Remove musica da playlist."""
        try:
            usuario = db.session.get(User, usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario nao encontrado'}

            playlist = PlaylistController._query_playlist_by_tenant(playlist_id, usuario.tenant_id)
            if not playlist:
                return {'success': False, 'message': 'Playlist nao encontrada'}
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}

            musica = db.session.get(Music, musica_id)
            if not musica:
                return {'success': False, 'message': 'Musica nao encontrada'}
            if not playlist.tem_musica(musica):
                return {'success': False, 'message': 'Musica nao esta na playlist'}

            playlist.remover_musica(musica)
            db.session.commit()
            return {
                'success': True,
                'message': 'Musica removida da playlist',
                'playlist': playlist.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao remover musica: {str(e)}'}

    @staticmethod
    def obter_playlists_publicas(limite=20, tenant_id=None):
        """Obtem playlists publicas do tenant resolvido."""
        try:
            tenant_resolvido = PlaylistController._resolve_tenant_id(tenant_id=tenant_id)
            query = Playlist.query.filter_by(publica=True)
            if tenant_resolvido is not None:
                query = query.filter_by(tenant_id=tenant_resolvido)

            playlists = query.order_by(Playlist.data_criacao.desc()).limit(limite).all()
            return {'success': True, 'playlists': [p.to_dict() for p in playlists]}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlists publicas: {str(e)}'}
