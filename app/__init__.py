import os

from flask import Flask

from app.config.settings import config
from app.extensions import init_extensions


def create_app(config_name=None):
    app = Flask(__name__)

    selected_config = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config.get(selected_config, config['default']))

    if app.config.get('SQLALCHEMY_DATABASE_URI') is None:
        raise ValueError('SQLALCHEMY_DATABASE_URI não configurado para o ambiente atual.')

    # Inicializa extensões
    init_extensions(app)

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
