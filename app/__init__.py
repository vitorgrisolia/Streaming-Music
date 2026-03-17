import os

from flask import Flask

from app.config.settings import config
from app.extensions import init_extensions


def _build_app_initials(app_name):
    parts = [part[0].upper() for part in app_name.split() if part and part[0].isalnum()]
    return ''.join(parts[:2]) or 'SM'


def create_app(config_name=None):
    app = Flask(__name__)

    selected_config = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config.get(selected_config, config['default']))

    if app.config.get('SQLALCHEMY_DATABASE_URI') is None:
        raise ValueError('SQLALCHEMY_DATABASE_URI nao configurado para o ambiente atual.')

    # Inicializa extensoes
    init_extensions(app)

    @app.context_processor
    def inject_app_identity():
        app_name = app.config.get('APP_NAME', 'Vitorando Music')
        return {
            'APP_NAME': app_name,
            'APP_INITIALS': _build_app_initials(app_name),
        }

    # Registra blueprints
    from app.views.auth_routes import auth_bp
    from app.views.music_routes import music_bp
    from app.views.playlist_routes import playlist_bp
    from app.views.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(music_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
