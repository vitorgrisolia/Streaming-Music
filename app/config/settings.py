import os
from pathlib import Path
from datetime import timedelta
from secrets import token_hex
from dotenv import load_dotenv

load_dotenv()


def _get_secret_key() -> str:
    """Retorna SECRET_KEY estável entre processos quando variável de ambiente não está definida."""
    env_secret = os.getenv('SECRET_KEY')
    if env_secret:
        return env_secret

    fallback_file = Path(__file__).resolve().parents[2] / '.secret_key'
    if fallback_file.exists():
        return fallback_file.read_text(encoding='utf-8').strip()

    fallback_key = token_hex(32)
    fallback_file.write_text(fallback_key, encoding='utf-8')
    try:
        os.chmod(fallback_file, 0o600)
    except OSError:
        pass
    return fallback_key

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = _get_secret_key()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}
    
    # Configurações de paginação
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/music_platform_dev'
    )


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
