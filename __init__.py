import os
import sys

from flask import Flask

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config.settings import config
from app.extensions import init_extensions, login_manager
from app.models import User


def _build_app_initials(app_name):
    parts = [part[0].upper() for part in app_name.split() if part and part[0].isalnum()]
    return ''.join(parts[:2]) or 'SM'


def create_app(config_name=None):
    """Factory para criacao da aplicacao Flask"""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializa extensoes
    init_extensions(app)

    @app.context_processor
    def inject_app_identity():
        app_name = app.config.get('APP_NAME', 'Vitorando Music')
        return {
            'APP_NAME': app_name,
            'APP_INITIALS': _build_app_initials(app_name),
        }

    # Configuracao do user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registra blueprints
    register_blueprints(app)

    # Cria diretorio de uploads se nao existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


def register_blueprints(app):
    """Registra todos os blueprints da aplicacao"""

    from app.views.auth_routes import auth_bp
    from app.views.music_routes import music_bp
    from app.views.playlist_routes import playlist_bp
    from app.views.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
