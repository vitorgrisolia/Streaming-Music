# app/__init__.py
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streaming_music.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa extensões
    db.init_app(app)
    
    # Registra blueprints
    with app.app_context():
        from app.views import auth_routes, music_routes, playlist_routes, api_routes
        
        # Registre seus blueprints aqui se estiver usando
        # app.register_blueprint(auth_routes.bp)
        # app.register_blueprint(music_routes.bp)
        # etc.
        
        # Cria tabelas se não existirem
        db.create_all()
    
    return app