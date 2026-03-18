import smtplib
from email.message import EmailMessage

from flask import current_app


class EmailServiceError(Exception):
    """Erro no envio de e-mail."""


class EmailService:
    """Servico SMTP para e-mails transacionais."""

    @staticmethod
    def _is_enabled():
        return bool(current_app.config.get('EMAIL_DELIVERY_ENABLED', False))

    @staticmethod
    def _build_link(path, token):
        base_url = (current_app.config.get('APP_BASE_URL') or 'http://localhost:5000').rstrip('/')
        return f"{base_url}{path}?token={token}"

    @staticmethod
    def send_email(to_email, subject, text_body):
        if not EmailService._is_enabled():
            return {'success': True, 'message': 'Envio de e-mail desabilitado por configuracao'}

        host = current_app.config.get('SMTP_HOST')
        port = int(current_app.config.get('SMTP_PORT', 587))
        username = current_app.config.get('SMTP_USERNAME')
        password = current_app.config.get('SMTP_PASSWORD')
        use_tls = bool(current_app.config.get('SMTP_USE_TLS', True))
        use_ssl = bool(current_app.config.get('SMTP_USE_SSL', False))
        mail_from = current_app.config.get('MAIL_FROM') or 'no-reply@streamingmusic.local'

        if not host:
            raise EmailServiceError('SMTP_HOST nao configurado')

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = to_email
        msg.set_content(text_body)

        try:
            if use_ssl:
                with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
                    if username and password:
                        smtp.login(username, password)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=20) as smtp:
                    smtp.ehlo()
                    if use_tls:
                        smtp.starttls()
                        smtp.ehlo()
                    if username and password:
                        smtp.login(username, password)
                    smtp.send_message(msg)
        except Exception as exc:
            raise EmailServiceError(f'Falha ao enviar e-mail: {exc}') from exc

        return {'success': True}

    @staticmethod
    def send_email_verification(to_email, token):
        link = EmailService._build_link('/auth/verificar-email', token)
        app_name = current_app.config.get('APP_NAME', 'Streaming Music')
        subject = f'[{app_name}] Verifique seu e-mail'
        text = (
            f'Bem-vindo ao {app_name}.\n\n'
            f'Clique no link para verificar seu e-mail:\n{link}\n\n'
            'Se voce nao solicitou este cadastro, ignore esta mensagem.'
        )
        return EmailService.send_email(to_email=to_email, subject=subject, text_body=text)

    @staticmethod
    def send_password_reset(to_email, token):
        link = EmailService._build_link('/auth/redefinir-senha', token)
        app_name = current_app.config.get('APP_NAME', 'Streaming Music')
        subject = f'[{app_name}] Reset de senha'
        text = (
            f'Voce solicitou redefinicao de senha no {app_name}.\n\n'
            f'Use o link para redefinir sua senha:\n{link}\n\n'
            'Se voce nao solicitou, ignore esta mensagem.'
        )
        return EmailService.send_email(to_email=to_email, subject=subject, text_body=text)
