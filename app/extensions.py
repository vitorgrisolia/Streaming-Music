import logging
from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from flask import g, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
cors = CORS()

_rate_limit_lock = Lock()
_rate_limit_buckets = defaultdict(deque)


def _configure_logging(app):
    if not app.logger.handlers:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)


def _init_sentry_if_available(app):
    sentry_dsn = app.config.get('SENTRY_DSN')
    if not sentry_dsn:
        return
    try:
        import sentry_sdk  # type: ignore
    except ImportError:
        app.logger.warning('SENTRY_DSN configurado, mas sentry-sdk nao esta instalado.')
        return

    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)
    app.logger.info('Sentry inicializado para observabilidade de erros.')


def _register_request_observability(app):
    @app.before_request
    def _mark_request_start():
        g._request_start_ts = monotonic()

    @app.after_request
    def _log_request(response):
        start = getattr(g, '_request_start_ts', None)
        if start is None:
            return response

        duration_ms = (monotonic() - start) * 1000
        response.headers['X-Request-Duration-Ms'] = f'{duration_ms:.2f}'
        app.logger.info(
            'request method=%s path=%s status=%s duration_ms=%.2f',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response


def _is_rate_limited(identifier, limit_per_minute):
    now = monotonic()
    window_seconds = 60
    with _rate_limit_lock:
        bucket = _rate_limit_buckets[identifier]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit_per_minute:
            return True
        bucket.append(now)
    return False


def _register_rate_limiting(app):
    @app.before_request
    def _guard_rate_limit():
        if not app.config.get('RATE_LIMIT_ENABLED', True):
            return None
        if not request.path.startswith('/api/'):
            return None
        if request.path == '/api/billing/webhook':
            return None

        endpoint = request.endpoint or 'unknown'
        if current_user.is_authenticated:
            identifier = f'user:{current_user.id}:{endpoint}'
        else:
            ip = request.remote_addr or 'unknown'
            identifier = f'ip:{ip}:{endpoint}'

        limit_per_minute = int(app.config.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 120))
        if _is_rate_limited(identifier, limit_per_minute):
            return (
                jsonify(
                    {
                        'success': False,
                        'message': 'Limite de requisicoes excedido. Tente novamente em instantes.',
                    }
                ),
                429,
            )
        return None


def init_extensions(app):
    """Inicializa extensoes com a aplicacao Flask."""
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faca login para acessar esta pagina.'
    login_manager.login_message_category = 'info'

    _configure_logging(app)
    _init_sentry_if_available(app)
    _register_request_observability(app)
    _register_rate_limiting(app)


@login_manager.user_loader
def load_user(user_id):
    """Recarrega usuario autenticado a partir do ID salvo na sessao."""
    from app.models import User

    return db.session.get(User, int(user_id))
