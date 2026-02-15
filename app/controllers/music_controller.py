from app.extensions import db
from app.models import Music, Album, Artist
from sqlalchemy import or_, func

class MusicController:
    """Controller para gerenciamento de músicas"""
    
    @staticmethod
    def buscar_musicas(termo=None, limite=50, offset=0):
        """Busca músicas por termo"""
        try:
            query = Music.query.join(Album).join(Artist)
            
            if termo:
                termo = f"%{termo}%"
                query = query.filter(
                    or_(
                        Music.titulo.ilike(termo),
                        Album.titulo.ilike(termo),
                        Artist.nome.ilike(termo)
                    )
                )
            
            total = query.count()
            musicas = query.order_by(Music.titulo).limit(limite).offset(offset).all()
            
            return {
                'success': True,
                'musicas': [m.to_dict() for m in musicas],
                'total': total,
                'limite': limite,
                'offset': offset
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao buscar músicas: {str(e)}'}
    
    @staticmethod
    def obter_musica(musica_id):
        """Obtém detalhes de uma música"""
        try:
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            return {
                'success': True,
                'musica': musica.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter música: {str(e)}'}
    
    @staticmethod
    def criar_musica(dados):
        """Cria nova música"""
        try:
            # Validações
            campos_obrigatorios = ['titulo', 'album_id', 'arquivo_url']
            for campo in campos_obrigatorios:
                if campo not in dados or not dados[campo]:
                    return {'success': False, 'message': f'Campo {campo} é obrigatório'}
            
            # Verifica se álbum existe
            album = Album.query.get(dados['album_id'])
            if not album:
                return {'success': False, 'message': 'Álbum não encontrado'}
            
            musica = Music(
                titulo=dados['titulo'],
                album_id=dados['album_id'],
                arquivo_url=dados['arquivo_url'],
                duracao=dados.get('duracao'),
                numero_faixa=dados.get('numero_faixa')
            )
            
            db.session.add(musica)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Música criada com sucesso',
                'musica': musica.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao criar música: {str(e)}'}
    
    @staticmethod
    def atualizar_musica(musica_id, dados):
        """Atualiza música existente"""
        try:
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            if 'titulo' in dados:
                musica.titulo = dados['titulo']
            if 'duracao' in dados:
                musica.duracao = dados['duracao']
            if 'numero_faixa' in dados:
                musica.numero_faixa = dados['numero_faixa']
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Música atualizada com sucesso',
                'musica': musica.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao atualizar música: {str(e)}'}
    
    @staticmethod
    def deletar_musica(musica_id):
        """Deleta música"""
        try:
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            db.session.delete(musica)
            db.session.commit()
            
            return {'success': True, 'message': 'Música deletada com sucesso'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao deletar música: {str(e)}'}
    
    @staticmethod
    def obter_musicas_populares(limite=20):
        """Retorna músicas mais populares"""
        try:
            musicas = Music.query.order_by(
                Music.visualizacoes.desc()
            ).limit(limite).all()
            
            return {
                'success': True,
                'musicas': [m.to_dict() for m in musicas]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter músicas populares: {str(e)}'}
    
    @staticmethod
    def registrar_reproducao(musica_id):
        """Registra reprodução de música"""
        try:
            musica = Music.query.get(musica_id)
            
            if not musica:
                return {'success': False, 'message': 'Música não encontrada'}
            
            musica.incrementar_visualizacao()
            
            return {
                'success': True,
                'visualizacoes': musica.visualizacoes
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao registrar reprodução: {str(e)}'}