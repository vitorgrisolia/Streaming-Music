from flask_login import login_user, logout_user
from app.extensions import db
from app.models import User
import re

class AuthController:
    """Controller para autenticação de usuários"""
    
    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_senha(senha):
        """Valida força da senha"""
        if len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres"
        return True, "Senha válida"
    
    @staticmethod
    def registrar_usuario(nome, email, senha):
        """Registra um novo usuário"""
        try:
            # Validações
            if not nome or len(nome.strip()) < 3:
                return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
            
            if not AuthController.validar_email(email):
                return {'success': False, 'message': 'Email inválido'}
            
            valido, mensagem = AuthController.validar_senha(senha)
            if not valido:
                return {'success': False, 'message': mensagem}
            
            # Verifica se email já existe
            if User.query.filter_by(email=email.lower()).first():
                return {'success': False, 'message': 'Email já cadastrado'}
            
            # Cria usuário
            usuario = User(
                nome=nome.strip(),
                email=email.lower(),
                senha=senha
            )
            
            db.session.add(usuario)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Usuário cadastrado com sucesso',
                'user': usuario.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao cadastrar: {str(e)}'}
    
    @staticmethod
    def fazer_login(email, senha, lembrar=False):
        """Autentica usuário"""
        try:
            usuario = User.query.filter_by(email=email.lower()).first()
            
            if not usuario:
                return {'success': False, 'message': 'Email ou senha incorretos'}
            
            if not usuario.ativo:
                return {'success': False, 'message': 'Usuário inativo'}
            
            if not usuario.check_password(senha):
                return {'success': False, 'message': 'Email ou senha incorretos'}
            
            login_user(usuario, remember=lembrar)
            
            return {
                'success': True,
                'message': 'Login realizado com sucesso',
                'user': usuario.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao fazer login: {str(e)}'}
    
    @staticmethod
    def fazer_logout():
        """Desconecta usuário"""
        try:
            logout_user()
            return {'success': True, 'message': 'Logout realizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao fazer logout: {str(e)}'}
    
    @staticmethod
    def atualizar_perfil(usuario, dados):
        """Atualiza perfil do usuário"""
        try:
            if 'nome' in dados and dados['nome']:
                if len(dados['nome'].strip()) < 3:
                    return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
                usuario.nome = dados['nome'].strip()
            
            if 'email' in dados and dados['email']:
                if not AuthController.validar_email(dados['email']):
                    return {'success': False, 'message': 'Email inválido'}
                
                email_existe = User.query.filter(
                    User.email == dados['email'].lower(),
                    User.id != usuario.id
                ).first()
                
                if email_existe:
                    return {'success': False, 'message': 'Email já está em uso'}
                
                usuario.email = dados['email'].lower()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Perfil atualizado com sucesso',
                'user': usuario.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao atualizar perfil: {str(e)}'}
    
    @staticmethod
    def alterar_senha(usuario, senha_atual, senha_nova):
        """Altera senha do usuário"""
        try:
            if not usuario.check_password(senha_atual):
                return {'success': False, 'message': 'Senha atual incorreta'}
            
            valido, mensagem = AuthController.validar_senha(senha_nova)
            if not valido:
                return {'success': False, 'message': mensagem}
            
            usuario.set_password(senha_nova)
            db.session.commit()
            
            return {'success': True, 'message': 'Senha alterada com sucesso'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao alterar senha: {str(e)}'}