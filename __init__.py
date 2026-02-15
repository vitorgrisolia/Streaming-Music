import os
from flask import Flask
from config.settings import config
from app.extensions import init_extensions, login_manager
from app.models import User

def create_app(config_name=None):
    """Factory para criação da aplicação Flask"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    init_extensions(app)
    
    # Configuração do user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registra blueprints
    register_blueprints(app)
    
    # Cria diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    from app.views.auth_routes import auth_bp
    from app.views.music_routes import music_bp
    from app.views.playlist_routes import playlist_bp
    from app.views.api_routes import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(api_bp, url_prefix='/api')