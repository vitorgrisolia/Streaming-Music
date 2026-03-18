import os
from datetime import timedelta
from secrets import token_hex

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, 'instance', 'streaming_music.db')


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


class Config:
    """Configuracao base da aplicacao."""

    APP_NAME = os.getenv('APP_NAME') or 'Vitorando Music'
    DEFAULT_TENANT_NAME = os.getenv('DEFAULT_TENANT_NAME') or 'Workspace Padrao'
    DEFAULT_TENANT_SLUG = os.getenv('DEFAULT_TENANT_SLUG') or 'default'
    SECRET_KEY = os.getenv('SECRET_KEY') or token_hex(32)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = _env_bool('SQLALCHEMY_ECHO', False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True

    WTF_CSRF_ENABLED = _env_bool('WTF_CSRF_ENABLED', True)
    REQUIRE_EMAIL_VERIFICATION = _env_bool('REQUIRE_EMAIL_VERIFICATION', False)
    AUTO_VERIFY_EMAIL = _env_bool('AUTO_VERIFY_EMAIL', False)
    PASSWORD_RESET_TOKEN_EXP_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_EXP_HOURS', '1'))

    RATE_LIMIT_ENABLED = _env_bool('RATE_LIMIT_ENABLED', True)
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '120'))
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_PRICE_ID_FREE = os.getenv('STRIPE_PRICE_ID_FREE')
    STRIPE_PRICE_ID_PRO = os.getenv('STRIPE_PRICE_ID_PRO')
    STRIPE_PRICE_ID_BUSINESS = os.getenv('STRIPE_PRICE_ID_BUSINESS')

    APP_BASE_URL = os.getenv('APP_BASE_URL') or 'http://localhost:5000'
    EMAIL_DELIVERY_ENABLED = _env_bool('EMAIL_DELIVERY_ENABLED', False)
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = _env_bool('SMTP_USE_TLS', True)
    SMTP_USE_SSL = _env_bool('SMTP_USE_SSL', False)
    MAIL_FROM = os.getenv('MAIL_FROM') or 'no-reply@streamingmusic.local'

    FREE_PLAN_PRIVATE_PLAYLIST_LIMIT = int(os.getenv('FREE_PLAN_PRIVATE_PLAYLIST_LIMIT', '1'))

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Configuracao de desenvolvimento."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or f'sqlite:///{DEFAULT_SQLITE_PATH}'
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = _env_bool('WTF_CSRF_ENABLED', False)
    REQUIRE_EMAIL_VERIFICATION = _env_bool('REQUIRE_EMAIL_VERIFICATION', False)
    AUTO_VERIFY_EMAIL = _env_bool('AUTO_VERIFY_EMAIL', True)


class ProductionConfig(Config):
    """Configuracao de producao."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = _env_bool('WTF_CSRF_ENABLED', True)
    REQUIRE_EMAIL_VERIFICATION = _env_bool('REQUIRE_EMAIL_VERIFICATION', True)
    AUTO_VERIFY_EMAIL = False
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }


class TestingConfig(Config):
    """Configuracao de testes."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    REQUIRE_EMAIL_VERIFICATION = False
    AUTO_VERIFY_EMAIL = True
    RATE_LIMIT_ENABLED = False
    EMAIL_DELIVERY_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
