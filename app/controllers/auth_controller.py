import json
import re
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app, has_request_context, request
from flask_login import login_user, logout_user

from app.extensions import db
from app.models import AuditLog, Membership, Tenant, User
from app.services.email_service import EmailService, EmailServiceError

UTC = timezone.utc


class AuthController:
    """Controller para autenticacao e seguranca de conta."""

    @staticmethod
    def _registrar_evento_auditoria(evento, tenant_id=None, user_id=None, nivel='INFO', detalhes=None):
        try:
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                evento=evento,
                nivel=nivel,
                detalhe_json=json.dumps(detalhes or {}, ensure_ascii=False),
                ip_address=request.remote_addr if has_request_context() else None,
                user_agent=(request.user_agent.string[:255] if has_request_context() else None),
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def validar_email(email):
        """Valida formato de email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validar_senha(senha):
        """Valida forca da senha."""
        if len(senha) < 8:
            return False, 'A senha deve ter no minimo 8 caracteres'
        return True, 'Senha valida'

    @staticmethod
    def _resolve_or_create_tenant(tenant_slug=None):
        slug = (tenant_slug or Tenant.default_slug()).strip().lower()
        tenant = Tenant.query.filter_by(slug=slug).first()
        if tenant:
            return tenant

        tenant_name = current_app.config.get('DEFAULT_TENANT_NAME', 'Workspace Padrao')
        tenant = Tenant(nome=tenant_name, slug=slug, ativo=True)
        db.session.add(tenant)
        db.session.flush()
        return tenant

    @staticmethod
    def registrar_usuario(nome, email, senha, tenant_slug=None):
        """Registra um novo usuario."""
        normalized_email = (email or '').strip().lower()
        try:
            if not nome or len(nome.strip()) < 3:
                return {'success': False, 'message': 'Nome deve ter no minimo 3 caracteres'}
            if not normalized_email:
                return {'success': False, 'message': 'Email e obrigatorio'}
            if not senha:
                return {'success': False, 'message': 'Senha e obrigatoria'}
            if not AuthController.validar_email(normalized_email):
                return {'success': False, 'message': 'Email invalido'}

            valido, mensagem = AuthController.validar_senha(senha)
            if not valido:
                return {'success': False, 'message': mensagem}

            if User.query.filter_by(email=normalized_email).first():
                return {'success': False, 'message': 'Email ja cadastrado'}

            tenant = AuthController._resolve_or_create_tenant(tenant_slug)
            usuario = User(
                nome=nome.strip(),
                email=normalized_email,
                senha=senha,
                tenant_id=tenant.id,
            )

            if current_app.config.get('AUTO_VERIFY_EMAIL', False):
                usuario.email_verificado_em = datetime.now(UTC).replace(tzinfo=None)
                usuario.email_verificacao_token = None
            else:
                usuario.email_verificacao_token = secrets.token_urlsafe(32)

            db.session.add(usuario)
            db.session.flush()

            membership = Membership(
                tenant_id=tenant.id,
                user_id=usuario.id,
                role='owner',
                ativo=True,
            )
            db.session.add(membership)
            db.session.commit()

            AuthController._registrar_evento_auditoria(
                evento='auth.register',
                tenant_id=tenant.id,
                user_id=usuario.id,
                detalhes={'email': normalized_email},
            )

            response = {
                'success': True,
                'message': 'Usuario cadastrado com sucesso',
                'user': usuario.to_dict(),
                'verification_required': not usuario.email_verificado,
            }
            if not usuario.email_verificado and usuario.email_verificacao_token:
                try:
                    EmailService.send_email_verification(
                        to_email=usuario.email,
                        token=usuario.email_verificacao_token,
                    )
                    response['verification_email_sent'] = True
                except EmailServiceError as mail_error:
                    response['verification_email_sent'] = False
                    response['message'] = (
                        'Usuario cadastrado, mas houve falha ao enviar email de verificacao'
                    )
                    response['email_error'] = str(mail_error)

            if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
                response['email_verification_token'] = usuario.email_verificacao_token
            return response
        except Exception as e:
            db.session.rollback()
            AuthController._registrar_evento_auditoria(
                evento='auth.register.error',
                tenant_id=None,
                user_id=None,
                nivel='ERROR',
                detalhes={'email': normalized_email, 'erro': str(e)},
            )
            return {'success': False, 'message': f'Erro ao cadastrar: {str(e)}'}

    @staticmethod
    def fazer_login(email, senha, lembrar=False):
        """Autentica usuario."""
        normalized_email = (email or '').strip().lower()
        try:
            if not normalized_email or not senha:
                return {'success': False, 'message': 'Email e senha sao obrigatorios'}

            usuario = User.query.filter_by(email=normalized_email).first()
            if not usuario:
                AuthController._registrar_evento_auditoria(
                    evento='auth.login.failed',
                    nivel='WARN',
                    detalhes={'email': normalized_email, 'motivo': 'usuario_nao_encontrado'},
                )
                return {'success': False, 'message': 'Email ou senha incorretos'}
            if not usuario.ativo:
                AuthController._registrar_evento_auditoria(
                    evento='auth.login.blocked',
                    tenant_id=usuario.tenant_id,
                    user_id=usuario.id,
                    nivel='WARN',
                    detalhes={'motivo': 'usuario_inativo'},
                )
                return {'success': False, 'message': 'Usuario inativo'}
            if current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False) and not usuario.email_verificado:
                AuthController._registrar_evento_auditoria(
                    evento='auth.login.blocked',
                    tenant_id=usuario.tenant_id,
                    user_id=usuario.id,
                    nivel='WARN',
                    detalhes={'motivo': 'email_nao_verificado'},
                )
                return {'success': False, 'message': 'Verifique seu email antes de fazer login'}
            if not usuario.check_password(senha):
                AuthController._registrar_evento_auditoria(
                    evento='auth.login.failed',
                    tenant_id=usuario.tenant_id,
                    user_id=usuario.id,
                    nivel='WARN',
                    detalhes={'motivo': 'senha_incorreta'},
                )
                return {'success': False, 'message': 'Email ou senha incorretos'}

            login_user(usuario, remember=lembrar)
            AuthController._registrar_evento_auditoria(
                evento='auth.login.success',
                tenant_id=usuario.tenant_id,
                user_id=usuario.id,
            )
            return {
                'success': True,
                'message': 'Login realizado com sucesso',
                'user': usuario.to_dict(),
            }
        except Exception as e:
            return {'success': False, 'message': f'Erro ao fazer login: {str(e)}'}

    @staticmethod
    def fazer_logout():
        """Desconecta usuario."""
        try:
            logout_user()
            return {'success': True, 'message': 'Logout realizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao fazer logout: {str(e)}'}

    @staticmethod
    def atualizar_perfil(usuario, dados):
        """Atualiza perfil do usuario."""
        try:
            if 'nome' in dados and dados['nome']:
                if len(dados['nome'].strip()) < 3:
                    return {'success': False, 'message': 'Nome deve ter no minimo 3 caracteres'}
                usuario.nome = dados['nome'].strip()

            if 'email' in dados and dados['email']:
                novo_email = dados['email'].lower().strip()
                if not AuthController.validar_email(novo_email):
                    return {'success': False, 'message': 'Email invalido'}

                email_existe = User.query.filter(User.email == novo_email, User.id != usuario.id).first()
                if email_existe:
                    return {'success': False, 'message': 'Email ja esta em uso'}

                usuario.email = novo_email
                usuario.email_verificado_em = None
                usuario.email_verificacao_token = secrets.token_urlsafe(32)

            db.session.commit()
            if usuario.email_verificacao_token:
                try:
                    EmailService.send_email_verification(
                        to_email=usuario.email,
                        token=usuario.email_verificacao_token,
                    )
                except EmailServiceError:
                    pass
            AuthController._registrar_evento_auditoria(
                evento='auth.profile.updated',
                tenant_id=usuario.tenant_id,
                user_id=usuario.id,
            )
            return {
                'success': True,
                'message': 'Perfil atualizado com sucesso',
                'user': usuario.to_dict(),
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao atualizar perfil: {str(e)}'}

    @staticmethod
    def alterar_senha(usuario, senha_atual, senha_nova):
        """Altera senha do usuario."""
        try:
            if not usuario.check_password(senha_atual):
                return {'success': False, 'message': 'Senha atual incorreta'}

            valido, mensagem = AuthController.validar_senha(senha_nova)
            if not valido:
                return {'success': False, 'message': mensagem}

            usuario.set_password(senha_nova)
            db.session.commit()
            AuthController._registrar_evento_auditoria(
                evento='auth.password.changed',
                tenant_id=usuario.tenant_id,
                user_id=usuario.id,
            )
            return {'success': True, 'message': 'Senha alterada com sucesso'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao alterar senha: {str(e)}'}

    @staticmethod
    def verificar_email_token(token):
        """Confirma verificacao de email."""
        try:
            if not token:
                return {'success': False, 'message': 'Token obrigatorio'}

            usuario = User.query.filter_by(email_verificacao_token=token).first()
            if not usuario:
                return {'success': False, 'message': 'Token invalido'}

            usuario.email_verificado_em = datetime.now(UTC).replace(tzinfo=None)
            usuario.email_verificacao_token = None
            db.session.commit()

            AuthController._registrar_evento_auditoria(
                evento='auth.email.verified',
                tenant_id=usuario.tenant_id,
                user_id=usuario.id,
            )
            return {'success': True, 'message': 'Email verificado com sucesso'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao verificar email: {str(e)}'}

    @staticmethod
    def solicitar_reset_senha(email):
        """Gera token de reset (resposta neutra para evitar enumeracao de contas)."""
        normalized_email = (email or '').strip().lower()
        try:
            if not normalized_email:
                return {'success': False, 'message': 'Email e obrigatorio'}

            usuario = User.query.filter_by(email=normalized_email).first()
            if usuario:
                hours = int(current_app.config.get('PASSWORD_RESET_TOKEN_EXP_HOURS', 1))
                usuario.reset_senha_token = secrets.token_urlsafe(32)
                usuario.reset_senha_expira_em = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=hours)
                db.session.commit()

                AuthController._registrar_evento_auditoria(
                    evento='auth.password.reset.requested',
                    tenant_id=usuario.tenant_id,
                    user_id=usuario.id,
                )

                response = {
                    'success': True,
                    'message': 'Se o email existir, voce recebera instrucoes para redefinir a senha',
                }
                try:
                    EmailService.send_password_reset(
                        to_email=usuario.email,
                        token=usuario.reset_senha_token,
                    )
                    response['reset_email_sent'] = True
                except EmailServiceError as mail_error:
                    response['reset_email_sent'] = False
                    response['email_error'] = str(mail_error)

                if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
                    response['reset_token'] = usuario.reset_senha_token
                return response

            return {
                'success': True,
                'message': 'Se o email existir, voce recebera instrucoes para redefinir a senha',
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao solicitar reset de senha: {str(e)}'}

    @staticmethod
    def redefinir_senha(token, nova_senha):
        """Redefine senha usando token de recuperacao."""
        try:
            if not token or not nova_senha:
                return {'success': False, 'message': 'Token e nova senha sao obrigatorios'}

            valido, mensagem = AuthController.validar_senha(nova_senha)
            if not valido:
                return {'success': False, 'message': mensagem}

            usuario = User.query.filter_by(reset_senha_token=token).first()
            if not usuario:
                return {'success': False, 'message': 'Token invalido'}

            if not usuario.reset_senha_expira_em or usuario.reset_senha_expira_em < datetime.now(UTC).replace(tzinfo=None):
                return {'success': False, 'message': 'Token expirado'}

            usuario.set_password(nova_senha)
            usuario.reset_senha_token = None
            usuario.reset_senha_expira_em = None
            db.session.commit()

            AuthController._registrar_evento_auditoria(
                evento='auth.password.reset.completed',
                tenant_id=usuario.tenant_id,
                user_id=usuario.id,
            )
            return {'success': True, 'message': 'Senha redefinida com sucesso'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao redefinir senha: {str(e)}'}
