from app.extensions import db
from app.models import Playlist, Music

class PlaylistController:
    """Controller para gerenciamento de playlists"""
    
    @staticmethod
    def criar_playlist(usuario_id, nome, descricao=None, publica=False):
        """Cria nova playlist"""
        try:
            if not nome or len(nome.strip()) < 3:
                return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
            
            playlist = Playlist(
                usuario_id=usuario_id,
                nome=nome.strip(),
                descricao=descricao,
                publica=publica
            )
            
            db.session.add(playlist)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Playlist criada com sucesso',
                'playlist': playlist.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao criar playlist: {str(e)}'}
    
    @staticmethod
    def obter_playlists_usuario(usuario_id, include_musicas=False):
        """Obtém playlists de um usuário"""
        try:
            playlists = Playlist.query.filter_by(usuario_id=usuario_id).order_by(
                Playlist.data_criacao.desc()
            ).all()
            
            return {
                'success': True,
                'playlists': [p.to_dict(include_musicas=include_musicas) for p in playlists]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlists: {str(e)}'}
    
    @staticmethod
    def obter_playlist(playlist_id, usuario_id=None):
        """Obtém detalhes de uma playlist"""
        try:
            playlist = Playlist.query.get(playlist_id)
            
            if not playlist:
                return {'success': False, 'message': 'Playlist não encontrada'}
            
            # Verifica permissão (se não for pública, deve ser do usuário)
            if not playlist.publica and playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}
            
            return {
                'success': True,
                'playlist': playlist.to_dict(include_musicas=True)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlist: {str(e)}'}
    
    @staticmethod
    def atualizar_playlist(playlist_id, usuario_id, dados):
        """Atualiza playlist"""
        try:
            playlist = Playlist.query.get(playlist_id)
            
            if not playlist:
                return {'success': False, 'message': 'Playlist não encontrada'}
            
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}
            
            if 'nome' in dados and dados['nome']:
                if len(dados['nome'].strip()) < 3:
                    return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
                playlist.nome = dados['nome'].strip()
            
            if 'descricao' in dados:
                playlist.descricao = dados['descricao']
            
            if 'publica' in dados:
                playlist.publica = bool(dados['publica'])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Playlist atualizada com sucesso',
                'playlist': playlist.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao atualizar playlist: {str(e)}'}
    
    @staticmethod
    def deletar_playlist(playlist_id, usuario_id):
        """Deleta playlist"""
        try:
            playlist = Playlist.query.get(playlist_id)
            
            if not playlist:
                return {'success': False, 'message': 'Playlist não encontrada'}
            
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
        """Adiciona música à playlist"""
        try:
            playlist = Playlist.query.get(playlist_id)
            
            if not playlist:
                return {'success': False, 'message': 'Playlist não encontrada'}
            
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}
            
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            if playlist.tem_musica(musica):
                return {'success': False, 'message': 'Música já está na playlist'}
            
            playlist.adicionar_musica(musica, posicao)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Música adicionada à playlist',
                'playlist': playlist.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao adicionar música: {str(e)}'}
    
    @staticmethod
    def remover_musica(playlist_id, usuario_id, musica_id):
        """Remove música da playlist"""
        try:
            playlist = Playlist.query.get(playlist_id)
            
            if not playlist:
                return {'success': False, 'message': 'Playlist não encontrada'}
            
            if playlist.usuario_id != usuario_id:
                return {'success': False, 'message': 'Acesso negado'}
            
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            if not playlist.tem_musica(musica):
                return {'success': False, 'message': 'Música não está na playlist'}
            
            playlist.remover_musica(musica)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Música removida da playlist',
                'playlist': playlist.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao remover música: {str(e)}'}
    
    @staticmethod
    def obter_playlists_publicas(limite=20):
        """Obtém playlists públicas"""
        try:
            playlists = Playlist.query.filter_by(publica=True).order_by(
                Playlist.data_criacao.desc()
            ).limit(limite).all()
            
            return {
                'success': True,
                'playlists': [p.to_dict() for p in playlists]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter playlists públicas: {str(e)}'}